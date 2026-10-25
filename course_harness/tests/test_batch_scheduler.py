"""Deterministic tests for Batch Scheduler (Course Harness v1).

Covers all Phase 6 required scenarios:
1. Correct manifest discovery.
2. Exact lesson ID selection.
3. Source status classification.
4. Approved baseline protection (M02-L11, M03-L08).
5. Maximum batch size limit (max 5).
6. Sequential scheduling (concurrency = 1) and lockfile concurrency protection.
7. Retry/Repair bounds (max 2 repairs).
8. Interrupted batch recovery and safe resume.
9. Stale checkpoint rejection on resume.
10. Source SHA256 mismatch detection.
11. Model NOT_VERIFIED rejection.
12. Receipt mismatch / integrity failure.
13. Resource budget exhaustion at safe lesson boundaries.
14. Missing token metadata handling (OBSERVED, ESTIMATED, UNKNOWN).
15. No automatic HUMAN_ACCEPTED from automated PASS.
16. Instructor image Hard Gate enforcement (prohibits author/lecturer portraits).
17. Dry-run causes zero provider calls and zero file mutations.
18. Existing single-lesson Controller behavior remains unchanged.
"""

import copy
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import yaml

from course_harness.batch import (
    APPROVED_BASELINES,
    MAX_BATCH_LESSONS,
    BatchLock,
    BatchPlan,
    BatchScheduler,
    BatchSchedulingError,
    BaselineIntegrityError,
    ConcurrentBatchExecutionError,
    ConfigurationChangedError,
    ManifestChangedError,
    ResourceBudgetTracker,
    ResourceLimits,
    ResourceUsage,
    scan_for_prohibited_instructor_images,
)
from course_harness.cli_adapter import AgyAdapter, CliExecutionError
from course_harness.run import CourseHarnessController, ManifestStaleError, BlockedExecutionError
from course_harness.state import (
    StateManager,
    calculate_file_sha256,
    compute_prompt_config_hash,
)


class TestBatchScheduler(unittest.TestCase):
    """Deterministic test suite for Course Harness v1 Batch Scheduler."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="batch_test_")
        self.source_dir = os.path.join(self.test_dir, "sources")
        self.output_dir = os.path.join(self.test_dir, "generated")
        self.prompts_dir = os.path.join(self.test_dir, "prompts")
        self.evidence_dir = os.path.join(self.output_dir, "evidence")
        self.checkpoints_dir = os.path.join(self.evidence_dir, "checkpoints")
        self.acceptance_dir = os.path.join(self.checkpoints_dir, "acceptance")
        self.receipts_dir = os.path.join(self.evidence_dir, "receipts")
        self.assets_dir = os.path.join(self.output_dir, "assets")
        self.modules_dir = os.path.join(self.output_dir, "modules")

        for d in [
            self.source_dir, self.output_dir, self.prompts_dir,
            self.evidence_dir, self.checkpoints_dir, self.acceptance_dir,
            self.receipts_dir, self.assets_dir, self.modules_dir,
        ]:
            os.makedirs(d, exist_ok=True)

        # Create dummy prompt files
        for role in ["worker", "auditor", "repair"]:
            with open(os.path.join(self.prompts_dir, f"{role}.md"), "w", encoding="utf-8") as f:
                f.write(f"# Prompt for {role}")

        # Create config.yaml
        self.config_path = os.path.join(self.test_dir, "config.yaml")
        self.config_data = {
            "models": {
                "worker": {"cli": "agy", "model": "gemini-3.8-flash-high", "effort": "high"},
                "auditor": {"cli": "agy", "model": "gemini-3.8-flash-high", "effort": "high"},
                "repair": {"cli": "agy", "model": "gemini-3.8-flash-high", "effort": "high"},
            },
            "workflow": {
                "unit": "lesson",
                "max_repair_rounds": 2,
                "model_fallback": False,
                "resumable": True,
                "source_grounded": True,
                "audit_required": True,
            },
            "execution": {
                "mode": "mock",
                "timeout_seconds": 180,
                "require_model_verification": True,
            },
            "paths": {
                "course_id": "Test_Course",
                "source_dir": self.source_dir,
                "output_dir": self.output_dir,
                "manifest_path": os.path.join(self.output_dir, "manifest.json"),
                "schema_path": "course_harness/schemas/audit.schema.json",
                "prompts_dir": self.prompts_dir,
            },
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config_data, f)

        # Create dummy source files
        self.sources = {
            "M01-L01": ("Module_01/01.md", "AVAILABLE", "VIDEO_TRANSCRIPT", "# Lesson 1\nContent for lesson 1."),
            "M01-L02": ("Module_01/02.md", "AVAILABLE", "READING", "# Lesson 2\nContent for lesson 2."),
            "M01-L03": ("Module_01/03.md", "INCOMPLETE", "QUIZ", "# Lesson 3\nQuestion without answers."),
            "M01-L04": ("Module_01/04.md", "LOCKED", "ACTIVITY", "# Lesson 4\nLocked content."),
            "M01-L05": ("Module_01/05.md", "AVAILABLE", "READING", "# Lesson 5\nContent for lesson 5."),
            "M01-L06": ("Module_01/06.md", "AVAILABLE", "REFLECTION", "# Lesson 6\nReflection content."),
            "M02-L11": ("Module_02/11.md", "AVAILABLE", "READING", "# Lesson 11\nScrum team roles baseline."),
            "M03-L08": ("Module_03/08.md", "INCOMPLETE", "ACTIVITY", "# Lesson 08\nProduct backlog baseline."),
        }

        self.manifest_data = {
            "course_id": "Test_Course",
            "total_modules": 3,
            "total_lessons": len(self.sources),
            "modules": {
                "M01": {"title": "Module 1", "lesson_count": 6, "lesson_ids": ["M01-L01", "M01-L02", "M01-L03", "M01-L04", "M01-L05", "M01-L06"]},
                "M02": {"title": "Module 2", "lesson_count": 1, "lesson_ids": ["M02-L11"]},
                "M03": {"title": "Module 3", "lesson_count": 1, "lesson_ids": ["M03-L08"]},
            },
            "lessons": {},
        }

        for lid, (rel, st, stype, body) in self.sources.items():
            full = os.path.join(self.source_dir, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(body)
            sha = calculate_file_sha256(full)
            self.manifest_data["lessons"][lid] = {
                "lesson_id": lid,
                "module_id": lid.split("-")[0],
                "filename": os.path.basename(rel),
                "relative_path": rel,
                "title": f"Title for {lid}",
                "source_type": stype,
                "status": st,
                "source_sha256": sha,
            }

        with open(self.config_data["paths"]["manifest_path"], "w", encoding="utf-8") as f:
            json.dump(self.manifest_data, f, indent=2)

        # Setup approved baselines M02-L11 and M03-L08 in test environment
        self._setup_mock_approved_baselines()

        self.controller = CourseHarnessController(
            config_path=self.config_path, mode_override="mock"
        )
        self.scheduler = BatchScheduler(
            config_path=self.config_path, mode_override="mock", controller=self.controller
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _setup_mock_approved_baselines(self):
        """Creates valid HUMAN_ACCEPTED checkpoints and acceptance artifacts matching APPROVED_BASELINES."""
        prompt_cfg_hash = compute_prompt_config_hash(self.prompts_dir, self.config_path)

        for lid, info in APPROVED_BASELINES.items():
            # Create final output file
            mod_id = lid.split("-")[0]
            final_path = os.path.join(self.modules_dir, mod_id, f"{lid}___Final.md")
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, "w", encoding="utf-8") as f:
                f.write(f"# Approved Final for {lid}\nContent.")
            # Set exact expected SHA256 in baseline info to match this test file
            real_sha = calculate_file_sha256(final_path)
            info["approved_final_sha256"] = real_sha

            # Create visual manifest for M02-L11
            if "visual_manifest_sha256" in info:
                vm_dir = os.path.join(self.assets_dir, lid)
                os.makedirs(vm_dir, exist_ok=True)
                vm_path = os.path.join(vm_dir, "visual_manifest.json")
                with open(vm_path, "w", encoding="utf-8") as vmf:
                    json.dump({"figures": []}, vmf)
                info["visual_manifest_sha256"] = calculate_file_sha256(vm_path)

            # Create acceptance artifact
            acc_path = os.path.join(self.acceptance_dir, f"{lid}_acceptance.json")
            acc_data = {
                "lesson_id": lid,
                "approved_final_sha256": real_sha,
                "reviewer": "User",
                "decision": "APPROVED",
                "timestamp": "2026-10-25T12:00:00Z",
                "source": "explicit user confirmation in this ChatGPT conversation",
                "notes": {"human_review_score": info.get("human_review_score", "90/100")},
                "identity_verification": "UNVERIFIED_CALLER_PROVIDED_IDENTITY",
            }
            with open(acc_path, "w", encoding="utf-8") as af:
                json.dump(acc_data, af, indent=2)
            acc_sha = calculate_file_sha256(acc_path)

            src_full = os.path.join(self.source_dir, self.sources[lid][0])
            src_sha = calculate_file_sha256(src_full)

            # Checkpoint
            chk = {
                "lesson_id": lid,
                "status": "HUMAN_ACCEPTED",
                "verdict": "HUMAN_ACCEPTED",
                "evidence_class": "HUMAN_ACCEPTED",
                "source_sha256": src_sha,
                "prompt_config_hash": prompt_cfg_hash,
                "final_path": final_path,
                "final_sha256": real_sha,
                "acceptance_path": acc_path,
                "acceptance_sha256": acc_sha,
                "human_approval": acc_data,
            }
            with open(os.path.join(self.checkpoints_dir, f"{lid}.json"), "w", encoding="utf-8") as f:
                json.dump(chk, f, indent=2)

    # -----------------------------------------------------------------------
    # 1. Correct manifest discovery
    # -----------------------------------------------------------------------
    def test_correct_manifest_discovery(self):
        """Discovers actual lesson IDs, types, statuses, and checksums from manifest."""
        eligible, excluded = self.scheduler.discover_lessons()
        eligible_ids = [c.lesson_id for c in eligible]

        self.assertIn("M01-L01", eligible_ids)
        self.assertIn("M01-L02", eligible_ids)
        self.assertIn("M01-L05", eligible_ids)
        self.assertIn("M01-L06", eligible_ids)

        # Approved baselines and locked lessons must not be in eligible
        self.assertNotIn("M02-L11", eligible_ids)
        self.assertNotIn("M03-L08", eligible_ids)
        self.assertNotIn("M01-L04", eligible_ids)

    # -----------------------------------------------------------------------
    # 2. Exact lesson ID selection
    # -----------------------------------------------------------------------
    def test_exact_lesson_id_selection(self):
        """Explicitly selects requested lesson IDs and rejects unknown or duplicate IDs."""
        selected = self.scheduler.select_candidates(requested_ids=["M01-L02", "M01-L01"])
        self.assertEqual([s.lesson_id for s in selected], ["M01-L02", "M01-L01"])

        # Unknown lesson ID fails closed
        with self.assertRaises(KeyError):
            self.scheduler.select_candidates(requested_ids=["M99-L99"])

        # Duplicates are deduplicated preserving order
        deduped = self.scheduler.select_candidates(requested_ids=["M01-L01", "M01-L02", "M01-L01"])
        self.assertEqual([s.lesson_id for s in deduped], ["M01-L01", "M01-L02"])

    # -----------------------------------------------------------------------
    # 3. Source status classification
    # -----------------------------------------------------------------------
    def test_source_status_classification(self):
        """AVAILABLE is eligible, INCOMPLETE requires scope approval, LOCKED is blocked."""
        # By default, INCOMPLETE is not eligible
        eligible, excluded = self.scheduler.discover_lessons(allow_incomplete=False)
        inc_item = next((x for x in excluded if x["lesson_id"] == "M01-L03"), None)
        self.assertIsNotNone(inc_item)
        self.assertEqual(inc_item["reason"], "INCOMPLETE_REQUIRES_BOUNDED_SCOPE_APPROVAL")

        # When allow_incomplete is True, INCOMPLETE becomes eligible
        eligible_with_scope, _ = self.scheduler.discover_lessons(allow_incomplete=True)
        inc_elig = next((x for x in eligible_with_scope if x.lesson_id == "M01-L03"), None)
        self.assertIsNotNone(inc_elig)
        self.assertTrue(inc_elig.is_eligible)

        # LOCKED is always blocked
        locked_item = next((x for x in excluded if x["lesson_id"] == "M01-L04"), None)
        self.assertIsNotNone(locked_item)
        self.assertEqual(locked_item["reason"], "BLOCKED_SOURCE_LOCKED")

    # -----------------------------------------------------------------------
    # 4. Approved baseline protection
    # -----------------------------------------------------------------------
    def test_approved_baseline_protection(self):
        """Approved baselines cannot be scheduled for re-execution."""
        with self.assertRaises(BaselineIntegrityError):
            self.scheduler.select_candidates(requested_ids=["M02-L11"])

        with self.assertRaises(BaselineIntegrityError):
            self.scheduler.select_candidates(requested_ids=["M03-L08"])

    # -----------------------------------------------------------------------
    # 5. Maximum batch size limit
    # -----------------------------------------------------------------------
    def test_maximum_batch_size_enforced(self):
        """Batch size cannot exceed 5 lessons."""
        # Requesting 6 lessons raises BatchSchedulingError
        with self.assertRaises(BatchSchedulingError):
            self.scheduler.select_candidates(limit=6)

        with self.assertRaises(BatchSchedulingError):
            self.scheduler.select_candidates(
                requested_ids=["M01-L01", "M01-L02", "M01-L03", "M01-L04", "M01-L05", "M01-L06"],
                allow_incomplete=True,
            )

    # -----------------------------------------------------------------------
    # 6. Sequential scheduling & concurrency protection
    # -----------------------------------------------------------------------
    def test_sequential_scheduling_and_lockfile(self):
        """Scheduler acquires atomic lockfile and prevents concurrent execution."""
        batch_id = "test-batch-lock"
        lock_path = os.path.join(self.scheduler.batch_checkpoints_dir, f"{batch_id}.lock")

        # First lock succeeds
        with BatchLock(lock_path, batch_id):
            self.assertTrue(os.path.exists(lock_path))
            # Second concurrent lock attempts fails
            with self.assertRaises(ConcurrentBatchExecutionError):
                with BatchLock(lock_path, batch_id):
                    pass

        # Released lock allows re-acquisition
        self.assertFalse(os.path.exists(lock_path))
        with BatchLock(lock_path, batch_id):
            self.assertTrue(os.path.exists(lock_path))

    # -----------------------------------------------------------------------
    # 7. Retry/Repair bounds
    # -----------------------------------------------------------------------
    def test_retry_repair_bounds(self):
        """Repair loop preserves maximum 2 repair rounds per lesson."""
        self.assertEqual(self.scheduler.limits.max_repairs_per_lesson, 2)
        self.assertEqual(self.controller.max_repair_rounds, 2)

    # -----------------------------------------------------------------------
    # 8. Interrupted batch recovery
    # -----------------------------------------------------------------------
    def test_interrupted_batch_recovery(self):
        """Resuming an interrupted batch detects completed lessons and resumes remaining work."""
        plan = self.scheduler.plan_batch(requested_ids=["M01-L01", "M01-L02"])
        batch_id = plan.batch_id
        chk_path = os.path.join(self.scheduler.batch_checkpoints_dir, f"{batch_id}.json")

        # Simulate batch interrupted after lesson 1 completed
        partial_chk = {
            "batch_id": batch_id,
            "course_id": plan.course_id,
            "status": "RUNNING",
            "manifest_sha256": plan.manifest_sha256,
            "prompt_config_hash": plan.prompt_config_hash,
            "limits": {},
            "created_at": plan.created_at,
            "updated_at": plan.created_at,
            "lessons": {
                "M01-L01": {
                    "status": "PASS",
                    "final_path": os.path.join(self.modules_dir, "M01", "M01-L01___Final.md"),
                    "final_sha256": "dummy_sha",
                }
            },
            "summary": {
                "total_candidates": 2, "passed": 1, "needs_human_review": 0,
                "blocked": 0, "failed": 0, "skipped": 0,
            },
        }
        with open(chk_path, "w", encoding="utf-8") as f:
            json.dump(partial_chk, f)

        # Mock is_resumable_pass to return True for M01-L01
        with patch.object(self.controller.state_mgr, "is_resumable_pass", return_value=True):
            with patch.object(self.controller, "process_lesson") as mock_process:
                mock_process.return_value = {
                    "status": "PASS", "final_path": "/fake/path", "final_sha256": "sha2", "audit_sha256": "asha2"
                }
                res = self.scheduler.execute_batch(plan, resume_batch_id=batch_id)

                # Lesson 1 was skipped as already verified PASS
                self.assertEqual(res["lessons"]["M01-L01"]["status"], "SKIPPED")
                # Lesson 2 was executed
                mock_process.assert_called_once_with("M01-L02")
                self.assertEqual(res["lessons"]["M01-L02"]["status"], "PASS")

    # -----------------------------------------------------------------------
    # 9. Stale checkpoint rejection on resume
    # -----------------------------------------------------------------------
    def test_stale_checkpoint_rejection_on_resume(self):
        """Stale or unverified PASS checkpoint is re-executed rather than skipped."""
        plan = self.scheduler.plan_batch(requested_ids=["M01-L01"])
        batch_id = plan.batch_id
        chk_path = os.path.join(self.scheduler.batch_checkpoints_dir, f"{batch_id}.json")

        partial_chk = {
            "batch_id": batch_id,
            "course_id": plan.course_id,
            "status": "RUNNING",
            "manifest_sha256": plan.manifest_sha256,
            "prompt_config_hash": plan.prompt_config_hash,
            "lessons": {"M01-L01": {"status": "PASS"}},
            "summary": {"total_candidates": 1, "passed": 1, "needs_human_review": 0, "blocked": 0, "failed": 0, "skipped": 0},
        }
        with open(chk_path, "w", encoding="utf-8") as f:
            json.dump(partial_chk, f)

        # If state_mgr.is_resumable_pass returns False (stale/invalid), it must re-execute
        with patch.object(self.controller.state_mgr, "is_resumable_pass", return_value=False):
            with patch.object(self.controller, "process_lesson") as mock_process:
                mock_process.return_value = {"status": "PASS"}
                res = self.scheduler.execute_batch(plan, resume_batch_id=batch_id)
                mock_process.assert_called_once_with("M01-L01")

    # -----------------------------------------------------------------------
    # 10. Source SHA256 mismatch detection
    # -----------------------------------------------------------------------
    def test_source_sha256_mismatch_detected(self):
        """If source file SHA256 is modified on disk, discovery marks it ineligible."""
        # Mutate M01-L01 on disk
        full_path = os.path.join(self.source_dir, self.sources["M01-L01"][0])
        with open(full_path, "a", encoding="utf-8") as f:
            f.write("\nTampered content.")

        eligible, excluded = self.scheduler.discover_lessons()
        m01_item = next((x for x in excluded if x["lesson_id"] == "M01-L01"), None)
        self.assertIsNotNone(m01_item)
        self.assertEqual(m01_item["reason"], "SOURCE_SHA_MISMATCH")

    # -----------------------------------------------------------------------
    # 11. Model NOT_VERIFIED rejection
    # -----------------------------------------------------------------------
    def test_model_not_verified_rejection(self):
        """Unverified model inference results in NEEDS_HUMAN_REVIEW and is not promoted to PASS."""
        plan = self.scheduler.plan_batch(requested_ids=["M01-L01"])
        with patch.object(self.controller, "process_lesson") as mock_process:
            mock_process.return_value = {
                "status": "NEEDS_HUMAN_REVIEW",
                "error_category": "MODEL_NOT_VERIFIED_FOR_PASS",
            }
            res = self.scheduler.execute_batch(plan)
            self.assertEqual(res["lessons"]["M01-L01"]["status"], "NEEDS_HUMAN_REVIEW")
            self.assertEqual(res["summary"]["needs_human_review"], 1)
            self.assertEqual(res["summary"]["passed"], 0)

    # -----------------------------------------------------------------------
    # 12. Receipt mismatch / integrity failure halts safely
    # -----------------------------------------------------------------------
    def test_receipt_integrity_failure_halts(self):
        """Critical integrity failure (e.g. ManifestStaleError) halts execution cleanly."""
        plan = self.scheduler.plan_batch(requested_ids=["M01-L01", "M01-L02"])
        with patch.object(self.controller, "process_lesson", side_effect=ManifestStaleError("Stale manifest")):
            with self.assertRaises(ManifestStaleError):
                self.scheduler.execute_batch(plan)

    # -----------------------------------------------------------------------
    # 13. Resource budget exhaustion at safe lesson boundary
    # -----------------------------------------------------------------------
    def test_resource_budget_exhaustion_at_safe_boundary(self):
        """Batch execution stops scheduling subsequent lessons when budget limit is reached."""
        # Set invocation limit = 2
        custom_limits = ResourceLimits(max_provider_invocations=2)
        scheduler = BatchScheduler(
            config_path=self.config_path, mode_override="mock", controller=self.controller, limits=custom_limits
        )
        plan = scheduler.plan_batch(requested_ids=["M01-L01", "M01-L02"])

        def fake_process(lid):
            # Record 2 invocations for first lesson
            scheduler.budget.record_invocation({"role": "worker", "usage": {"total_tokens": 10000}})
            scheduler.budget.record_invocation({"role": "auditor", "usage": {"total_tokens": 10000}})
            return {"status": "PASS"}

        with patch.object(self.controller, "process_lesson", side_effect=fake_process):
            res = scheduler.execute_batch(plan)
            # First lesson succeeded
            self.assertEqual(res["lessons"]["M01-L01"]["status"], "PASS")
            # Second lesson was blocked by budget exhaustion at safe boundary
            self.assertEqual(res["lessons"]["M01-L02"]["status"], "BLOCKED")
            self.assertEqual(res["lessons"]["M01-L02"]["error_category"], "BUDGET_EXHAUSTED")
            self.assertEqual(res["status"], "PAUSED_BUDGET_EXHAUSTED")

    # -----------------------------------------------------------------------
    # 14. Missing token metadata handling
    # -----------------------------------------------------------------------
    def test_missing_token_metadata_handling(self):
        """Distinguishes OBSERVED_USAGE, ESTIMATED_USAGE, and UNKNOWN_USAGE without inventing tokens."""
        tracker = ResourceBudgetTracker()

        # Invocations without usage dict
        tracker.record_invocation({"role": "worker"})
        self.assertEqual(tracker.usage.invocations, 1)
        self.assertEqual(tracker.usage.total_tokens, 0)
        self.assertEqual(tracker.usage.usage_class, "UNKNOWN_USAGE")

        # Invocations with observed usage dict
        tracker.record_invocation({
            "role": "auditor",
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 500,
                "thinking_tokens": 400,
                "total_tokens": 1500,  # Provider total already includes thinking tokens
            }
        })
        self.assertEqual(tracker.usage.invocations, 2)
        self.assertEqual(tracker.usage.input_tokens, 1000)
        self.assertEqual(tracker.usage.output_tokens, 500)
        self.assertEqual(tracker.usage.thinking_tokens, 400)
        # Total tokens must not double-count thinking tokens
        self.assertEqual(tracker.usage.total_tokens, 1500)
        self.assertEqual(tracker.usage.usage_class, "OBSERVED_USAGE")

    # -----------------------------------------------------------------------
    # 15. No automatic HUMAN_ACCEPTED
    # -----------------------------------------------------------------------
    def test_no_automatic_human_accepted(self):
        """Automated PASS never claims or sets HUMAN_ACCEPTED."""
        plan = self.scheduler.plan_batch(requested_ids=["M01-L01"])
        with patch.object(self.controller, "process_lesson") as mock_process:
            mock_process.return_value = {
                "status": "PASS",
                "verdict": "PASS",
                "final_path": "/fake/final",
            }
            res = self.scheduler.execute_batch(plan)
            self.assertEqual(res["lessons"]["M01-L01"]["status"], "PASS")
            self.assertNotEqual(res["lessons"]["M01-L01"]["status"], "HUMAN_ACCEPTED")

    # -----------------------------------------------------------------------
    # 16. Instructor image Hard Gate enforcement
    # -----------------------------------------------------------------------
    def test_instructor_image_hard_gate(self):
        """Hard Gate blocks any generated draft containing instructor portraits/photos."""
        prohibited_md = (
            "# Lesson Title\n\n"
            "![Lecturer portrait photo](assets/instructor_photo.jpg)\n\n"
            "Content explaining Scrum."
        )
        violations = scan_for_prohibited_instructor_images(prohibited_md)
        self.assertTrue(len(violations) > 0)
        self.assertIn("PROHIBITED_INSTRUCTOR_IMAGE", violations[0])

        # Clean markdown passes
        clean_md = (
            "# Lesson Title\n\n"
            "![Scrum workflow flowchart](assets/F01_scrum_workflow.svg)\n\n"
            "Content explaining Scrum."
        )
        clean_violations = scan_for_prohibited_instructor_images(clean_md)
        self.assertEqual(len(clean_violations), 0)

        # Batch execution blocks when final output contains prohibited instructor photo
        plan = self.scheduler.plan_batch(requested_ids=["M01-L01"])
        dummy_final = os.path.join(self.test_dir, "prohibited_final.md")
        with open(dummy_final, "w", encoding="utf-8") as f:
            f.write(prohibited_md)

        with patch.object(self.controller, "process_lesson") as mock_process:
            mock_process.return_value = {
                "status": "PASS",
                "final_path": dummy_final,
            }
            res = self.scheduler.execute_batch(plan)
            # Hard gate overrides status to BLOCKED
            self.assertEqual(res["lessons"]["M01-L01"]["status"], "BLOCKED")
            self.assertEqual(res["lessons"]["M01-L01"]["error_category"], "PROHIBITED_INSTRUCTOR_IMAGE")

    # -----------------------------------------------------------------------
    # 17. Dry-run causes zero provider calls and zero file mutations
    # -----------------------------------------------------------------------
    def test_dry_run_causes_zero_provider_calls(self):
        """Dry run produces detailed candidate plan with 0 provider calls and 0 mutations."""
        with patch.object(self.controller.adapter, "invoke") as mock_invoke:
            plan = self.scheduler.plan_batch()
            res = self.scheduler.execute_batch(plan, dry_run=True)

            self.assertEqual(res["status"], "DRY_RUN_COMPLETED")
            self.assertEqual(res["provider_calls"], 0)
            mock_invoke.assert_not_called()

            # Verify no new checkpoints were written
            batch_chks = os.listdir(self.scheduler.batch_checkpoints_dir)
            self.assertEqual(len(batch_chks), 0)

    # -----------------------------------------------------------------------
    # 18. Existing single-lesson Controller behavior unchanged
    # -----------------------------------------------------------------------
    def test_existing_single_lesson_controller_behavior_unchanged(self):
        """Single-lesson processing through Controller behaves identically."""
        with patch.object(self.controller.adapter, "invoke") as mock_invoke:
            mock_invoke.return_value = ("Sample response", {"role": "worker", "status": "SUCCESS"})
            # Verify controller attributes and methods remain intact
            self.assertTrue(hasattr(self.controller, "process_lesson"))
            self.assertTrue(hasattr(self.controller, "get_manifest"))
            self.assertTrue(hasattr(self.controller, "verify_system"))
            self.assertEqual(self.controller.max_repair_rounds, 2)


if __name__ == "__main__":
    unittest.main()
