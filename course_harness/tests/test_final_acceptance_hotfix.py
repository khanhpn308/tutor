"""Comprehensive Regression Tests for Course Harness v1 Final Acceptance Hotfix.

Covers:
- F-HF-01 (HIGH): Audit receipt provenance verification & mandatory model verification.
- F-HF-02 (HIGH): MOCK_PASS vs Production PASS isolation, evidence classification, and state invariants.
"""

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock, patch

import yaml

from course_harness.cli_adapter import (
    AgyAdapter,
    CliExecutionError,
    ModelUnavailableError,
)
from course_harness.run import CourseHarnessController
from course_harness.state import StateManager, calculate_file_sha256
from course_harness.validator import AuditValidator, ValidationError


class TestFinalAcceptanceHotfix(unittest.TestCase):
    """Deterministic regression tests for F-HF-01 and F-HF-02 findings."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.yaml")
        self.output_dir = os.path.join(self.test_dir, "generated")
        self.evidence_dir = os.path.join(self.output_dir, "evidence")
        self.checkpoints_dir = os.path.join(self.evidence_dir, "checkpoints")
        self.acceptance_dir = os.path.join(self.checkpoints_dir, "acceptance")
        self.receipts_dir = os.path.join(self.evidence_dir, "receipts")
        self.drafts_dir = os.path.join(self.output_dir, "drafts")
        self.audits_dir = os.path.join(self.output_dir, "audits")
        self.modules_dir = os.path.join(self.output_dir, "modules")

        for d in [
            self.output_dir,
            self.evidence_dir,
            self.checkpoints_dir,
            self.acceptance_dir,
            self.receipts_dir,
            self.drafts_dir,
            self.audits_dir,
            self.modules_dir,
        ]:
            os.makedirs(d, exist_ok=True)

        self.config_data = {
            "models": {
                "worker": {"model": "gemini-3.8-flash-high", "effort": "high"},
                "auditor": {"model": "gemini-3.8-flash-high", "effort": "high"},
                "repair": {"model": "gemini-3.8-flash-high", "effort": "high"},
            },
            "workflow": {"max_repair_rounds": 2},
            "execution": {
                "mode": "automated_cli",
                "agy_binary": "/bin/mock-agy",
                "timeout_seconds": 180,
                "require_model_verification": True,
            },
            "paths": {
                "course_id": "Agile_Project_Management",
                "source_dir": "output_course/Agile_Project_Management",
                "output_dir": self.output_dir,
                "prompts_dir": "course_harness/prompts",
                "schema_path": "course_harness/schemas/audit.schema.json",
            },
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config_data, f)

        self.state_mgr = StateManager(
            checkpoints_dir=self.checkpoints_dir,
            prompt_config_hash="hash_v1",
            acceptance_dir=self.acceptance_dir,
            schema_path="course_harness/schemas/audit.schema.json",
            receipts_dir=self.receipts_dir,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # Helper fixtures
    def _create_final_file(self, lesson_id: str, content: str = "# Final Lesson Markdown\n\nLesson text.") -> Tuple[str, str]:
        final_path = os.path.join(self.modules_dir, f"{lesson_id}_final.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(content)
        final_sha = calculate_file_sha256(final_path)
        self.state_mgr.initialize_lesson_state(lesson_id, source_sha256="src_sha_test")
        self.state_mgr.transition(lesson_id, "AUDITED", {"final_path": final_path, "final_sha256": final_sha})
        return final_path, final_sha

    def _create_audit_report(self, lesson_id: str, final_sha: str, inv_id: str, verdict: str = "PASS", findings: list = None, dim_scores: dict = None) -> Tuple[str, str]:
        audit_payload = {
            "lesson_id": lesson_id,
            "verdict": verdict,
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": (verdict == "PASS" and not findings),
            "summary": f"Audit report verdict {verdict}",
            "dimension_scores": dim_scores or {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "VISUAL_PEDAGOGY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": findings or [],
            "limitations": ["Deterministic test harness limitation"],
            "audited_final_sha256": final_sha,
            "audit_invocation_id": inv_id,
            "model_verification": "VERIFIED",
        }
        audit_path = os.path.join(self.audits_dir, f"{lesson_id}_audit_test.json")
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(audit_payload, f, indent=2)
        audit_sha = calculate_file_sha256(audit_path)
        return audit_path, audit_sha

    def _create_valid_receipt(
        self,
        invocation_id: str,
        lesson_id: str,
        final_sha: str,
        audit_sha: str,
        execution_mode: str = "automated_cli",
        provider: str = "agy",
        evidence_class: str = "REAL_AGY_VERIFIED",
        model_reported: str = "gemini-3.8-flash-high",
        model_verified: str = "VERIFIED",
        terminal_status: str = "SUCCESS",
        source_sha256: str = "src_sha_test",
        prompt_config_hash: str = "hash_v1",
        role: str = "auditor",
    ) -> Dict[str, Any]:
        receipt_data = {
            "invocation_id": invocation_id,
            "role": role,
            "lesson_id": lesson_id,
            "execution_mode": execution_mode,
            "provider": provider,
            "evidence_class": evidence_class,
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": model_reported,
            "model_verified": model_verified,
            "terminal_status": terminal_status,
            "audited_final_sha256": final_sha,
            "source_sha256": source_sha256,
            "prompt_config_hash": prompt_config_hash,
            "audit_report_sha256": audit_sha,
            "created_at": "2026-10-23T10:00:00Z",
        }
        self.state_mgr.save_audit_receipt(receipt_data)
        return receipt_data

    # =========================================================================
    # F-HF-01: Audit Receipt Provenance & Verification Tests
    # =========================================================================

    def test_valid_real_agy_audit_receipt_and_valid_audit_report_pass_eligible(self):
        """1. Valid real AGY audit receipt and valid audit report -> PASS eligible."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-test001"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        self._create_valid_receipt(inv_id, "M01-L07", final_sha, audit_sha)

        chk = self.state_mgr.record_audit_verdict(
            lesson_id="M01-L07",
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=inv_id,
        )
        self.assertEqual(chk["status"], "PASS")
        self.assertEqual(chk["verdict"], "PASS")
        self.assertEqual(chk["evidence_class"], "REAL_AGY_VERIFIED")
        self.assertTrue(self.state_mgr.is_resumable_pass("M01-L07", "src_sha_test"))

    def test_arbitrary_invocation_id_rejected(self):
        """2. Caller-supplied arbitrary invocation ID without Controller receipt -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, "fabricated-caller-id-999")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id="fabricated-caller-id-999",
            )
        self.assertIn("no controller audit receipt found", str(ctx.exception).lower())

    def test_missing_receipt_rejected(self):
        """3. Missing receipt -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, "inv-missing-receipt")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id="inv-missing-receipt",
            )
        self.assertIn("no controller audit receipt found", str(ctx.exception).lower())

    def test_receipt_from_another_lesson_rejected(self):
        """4. Receipt from another lesson -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M02-L11-att1-test002"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        # Receipt identifies M02-L11, not M01-L07
        self._create_valid_receipt(inv_id, "M02-L11", final_sha, audit_sha)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("lesson id mismatch", str(ctx.exception).lower())

    def test_receipt_from_worker_instead_of_auditor_rejected(self):
        """5. Receipt from Worker instead of Auditor -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-worker-M01-L07-att1-test003"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        # Receipt role is worker
        self._create_valid_receipt(inv_id, "M01-L07", final_sha, audit_sha, role="worker")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("invocation role is 'worker', expected 'auditor'", str(ctx.exception).lower())

    def test_receipt_bound_to_another_final_sha_rejected(self):
        """6. Receipt bound to another final SHA -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-test004"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        different_final_sha = hashlib.sha256(b"Different draft content").hexdigest()
        self._create_valid_receipt(inv_id, "M01-L07", different_final_sha, audit_sha)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("does not match final sha256", str(ctx.exception).lower())

    def test_receipt_bound_to_outdated_source_config_rejected(self):
        """7. Receipt bound to outdated source/config -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-test005"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        # Outdated prompt config hash
        self._create_valid_receipt(inv_id, "M01-L07", final_sha, audit_sha, prompt_config_hash="outdated_hash_v0")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("prompt_config_hash mismatch", str(ctx.exception).lower())

        # Also test source_sha mismatch
        inv_id2 = "inv-auditor-M01-L07-att1-test005b"
        audit_path2, audit_sha2 = self._create_audit_report("M01-L07", final_sha, inv_id2)
        self._create_valid_receipt(inv_id2, "M01-L07", final_sha, audit_sha2, source_sha256="outdated_source_sha")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path2,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id2,
            )
        self.assertIn("source_sha256 mismatch", str(ctx.exception).lower())

    def test_audit_report_checksum_mismatch_rejected(self):
        """8. Audit report checksum mismatch -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-test006"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        tampered_audit_sha = hashlib.sha256(b"Tampered report content").hexdigest()
        self._create_valid_receipt(inv_id, "M01-L07", final_sha, tampered_audit_sha)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("audit report checksum mismatch", str(ctx.exception).lower())

    def test_receipt_reports_wrong_model_rejected(self):
        """9. Receipt reports wrong model -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-test007"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        self._create_valid_receipt(inv_id, "M01-L07", final_sha, audit_sha, model_reported="gemini-1.5-flash")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("does not match required model", str(ctx.exception).lower())

    def test_receipt_lacks_required_model_verification_rejected(self):
        """10. Receipt lacks required model verification -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-test008"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        self._create_valid_receipt(inv_id, "M01-L07", final_sha, audit_sha, model_verified="NOT_VERIFIED")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("receipt lacks required model verification", str(ctx.exception).lower())

    def test_report_verdict_fail_caller_requests_pass_rejected(self):
        """11. Report verdict FAIL but caller requests PASS -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-test009"
        findings = [{
            "finding_id": "F-001",
            "severity": "HIGH",
            "category": "SOURCE_FIDELITY",
            "source_locator": "01:00",
            "draft_locator": "Sec 1",
            "description": "Hallucination",
            "required_action": "Fix hallucination",
        }]
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id, verdict="FAIL", findings=findings)
        self._create_valid_receipt(inv_id, "M01-L07", final_sha, audit_sha)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("audit verdict rejected", str(ctx.exception).lower())
        self.assertIn("authoritative report verdict is 'fail'", str(ctx.exception).lower())

    def test_caller_attempts_to_disable_mandatory_verification_rejected(self):
        """12. Caller attempts to disable mandatory verification -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-test010"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        self._create_valid_receipt(inv_id, "M01-L07", final_sha, audit_sha)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
                require_model_verification=False,
            )
        self.assertIn("cannot disable mandatory model verification", str(ctx.exception).lower())

    def test_historical_m03_l08_audit_reused_for_corrected_final_rejected(self):
        """13. Historical M03-L08 audit is reused for corrected final -> rejected."""
        final_path, final_sha = self._create_final_file("M03-L08", content="# Corrected final without 70% tree death claim")
        historical_audit_path = "generated_course/Agile_Project_Management/historical_pilot_v1/M03-L08/M03-L08_audit_v1.json"
        if not os.path.exists(historical_audit_path):
            historical_audit_path = "review_bundle/pilots/audits/M03-L08_audit_v1.json"
        self.assertTrue(os.path.exists(historical_audit_path))

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M03-L08",
                verdict="PASS",
                audit_path=historical_audit_path,
                expected_final_sha256=final_sha,
            )
        self.assertIn("lacks 'audited_final_sha256' binding", str(ctx.exception).lower())

    def test_mock_generated_receipt_submitted_as_real_agy_evidence_rejected(self):
        """14. Mock-generated receipt is submitted as real AGY evidence -> rejected."""
        final_path, final_sha = self._create_final_file("M01-L07")
        inv_id = "inv-auditor-M01-L07-att1-mock001"
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, inv_id)
        # Mock-generated receipt
        self._create_valid_receipt(
            inv_id,
            "M01-L07",
            final_sha,
            audit_sha,
            execution_mode="mock",
            provider="mock",
            evidence_class="MOCK_SIMULATED",
            model_verified="NOT_APPLICABLE",
            terminal_status="SIMULATED",
        )

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=inv_id,
            )
        self.assertIn("mock execution receipt cannot grant production pass", str(ctx.exception).lower())

    # =========================================================================
    # F-HF-02: MOCK_PASS vs Production PASS Isolation Tests
    # =========================================================================

    def test_mock_worker_plus_mock_auditor_succeeds_mock_pass_not_pass(self):
        """15. Mock Worker + Mock Auditor succeeds -> MOCK_PASS, not PASS."""
        controller = CourseHarnessController(self.config_path, mode_override="mock")
        res = controller.process_lesson("M01-L07", reset=True)

        self.assertEqual(res["status"], "MOCK_PASS")
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["evidence_class"], "MOCK_SIMULATED")
        self.assertNotEqual(res["status"], "PASS")

    def test_mock_worker_plus_mock_auditor_cannot_create_verified_agy_receipts(self):
        """16. Mock Worker + Mock Auditor cannot create verified AGY receipts."""
        controller = CourseHarnessController(self.config_path, mode_override="mock")
        res = controller.process_lesson("M01-L07", reset=True)

        inv_id = res.get("audit_invocation_id")
        self.assertIsNotNone(inv_id)
        receipt = controller.state_mgr.get_audit_receipt(inv_id)
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt["execution_mode"], "mock")
        self.assertEqual(receipt["evidence_class"], "MOCK_SIMULATED")
        self.assertEqual(receipt["model_verified"], "NOT_APPLICABLE")
        self.assertNotEqual(receipt["evidence_class"], "REAL_AGY_VERIFIED")
        self.assertNotEqual(receipt["model_verified"], "VERIFIED")

    def test_mock_model_verified_is_never_reported_as_real_verification(self):
        """17. Mock model_verified is never reported as real verification."""
        adapter = AgyAdapter(mode="mock", evidence_dir=self.evidence_dir)
        _, meta_w = adapter.invoke("prompt", "worker", "M01-L07")
        _, meta_a = adapter.invoke("prompt", "auditor", "M01-L07")
        _, meta_r = adapter.invoke("prompt", "repair", "M01-L07")

        for meta in [meta_w, meta_a, meta_r]:
            self.assertEqual(meta["model_verified"], "NOT_APPLICABLE")
            self.assertEqual(meta["evidence_class"], "MOCK_SIMULATED")
            self.assertEqual(meta["execution_mode"], "mock")
            self.assertNotEqual(meta["model_verified"], "VERIFIED")
        self.assertEqual(adapter.last_model_verified, "NOT_APPLICABLE")

    def test_mock_result_cannot_resume_as_production_pass(self):
        """18. Mock result cannot resume as production PASS."""
        controller = CourseHarnessController(self.config_path, mode_override="mock")
        res = controller.process_lesson("M01-L07", reset=True)
        self.assertEqual(res["status"], "MOCK_PASS")

        manifest = controller.get_manifest()
        src_sha = manifest["lessons"]["M01-L07"]["source_sha256"]
        self.assertFalse(controller.state_mgr.is_resumable_pass("M01-L07", src_sha))

    def test_mock_receipt_cannot_be_used_by_record_audit_verdict_to_grant_pass(self):
        """19. Mock receipt cannot be used by record_audit_verdict() to grant PASS."""
        controller = CourseHarnessController(self.config_path, mode_override="mock")
        res = controller.process_lesson("M01-L07", reset=True)
        inv_id = res["audit_invocation_id"]

        with self.assertRaises(ValueError) as ctx:
            controller.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=res["audit_path"],
                expected_final_sha256=res["final_sha256"],
                audit_invocation_id=inv_id,
            )
        self.assertIn("mock execution receipt cannot grant production pass", str(ctx.exception).lower())

    @patch("subprocess.run")
    def test_real_mode_controller_path_with_valid_mocked_subprocess_responses_satisfies_production_pass(self, mock_run):
        """20. Real-mode Controller path with valid mocked subprocess responses satisfies production PASS."""
        controller = CourseHarnessController(self.config_path, mode_override="automated_cli")
        controller.adapter.resolved_binary = "/bin/mock-agy"

        valid_draft_md = (
            "# Bài học M01-L07: Tuyên ngôn Agile\n\n"
            "## 1. Mục tiêu bài học (Learning Objectives)\n- Nắm vững 4 giá trị.\n\n"
            "## 2. Kiến thức nền tảng (Context)\n- Agile Scrum context.\n\n"
            "## 3. Nội dung lý thuyết trọng tâm\n- Cá nhân và tương tác hơn quy trình và công cụ.\n\n"
            "## 5. Bảng thuật ngữ chuyên ngành Anh - Việt\n| Term | Nghĩa | Ghi chú |\n| Agile | Linh hoạt | PP |\n\n"
            "## 6. Tóm tắt cốt lõi\n- Giá trị chính.\n\n"
            "## 8. Nguồn đối chiếu\n- [01:51] locator.\n"
        )
        draft_sha = hashlib.sha256(valid_draft_md.strip().encode("utf-8")).hexdigest()

        worker_env = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "conv-worker-real-001",
            "response": valid_draft_md,
            "usage": {"total_tokens": 500},
        }

        audit_payload = {
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": True,
            "summary": "Simulated real AGY audit pass",
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "VISUAL_PEDAGOGY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": [],
            "limitations": ["Simulated integration test fixture"],
            "audited_final_sha256": draft_sha,
            "model_verification": "VERIFIED",
        }

        auditor_env = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "conv-auditor-real-001",
            "response": json.dumps(audit_payload),
            "usage": {"total_tokens": 700},
        }

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=json.dumps(worker_env), stderr=""),
            MagicMock(returncode=0, stdout=json.dumps(auditor_env), stderr=""),
        ]

        res = controller.process_lesson("M01-L07", reset=True)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["evidence_class"], "REAL_AGY_VERIFIED")
        self.assertEqual(res["model_verified"], "VERIFIED")
        self.assertTrue(os.path.exists(res["final_path"]))
        self.assertTrue(controller.state_mgr.is_resumable_pass("M01-L07", res["source_sha256"]))

    @patch("subprocess.run")
    def test_missing_real_provider_evidence_blocks_production_pass(self, mock_run):
        """21. Missing real-provider evidence blocks production PASS."""
        controller = CourseHarnessController(self.config_path, mode_override="automated_cli")
        controller.adapter.resolved_binary = "/bin/mock-agy"

        # Worker succeeds with verified model
        worker_env = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "conv-w-001",
            "response": "# Valid lesson draft markdown with sufficient content for structure heuristics.\n\n## 1. Mục tiêu bài học (Learning Objectives)\n- Nắm vững kiến thức\n\n## 3. Nội dung lý thuyết trọng tâm (Theory)\n- Giải thích chi tiết...\n\n## 6. Tóm tắt cốt lõi (Key Takeaways)\n- Điểm 1\n\n## 8. Nguồn đối chiếu (Source Traceability)\n- Timestamp 01:51\n",
        }
        # Auditor envelope omits model!
        auditor_env = {
            "status": "SUCCESS",
            "conversation_id": "conv-a-001",
            "response": json.dumps({
                "lesson_id": "M01-L07",
                "verdict": "PASS",
                "quality_rubric_version": "2.0-visual-first",
                "content_quality_accepted": True,
                "summary": "Audited",
                "dimension_scores": {
                    "SOURCE_FIDELITY": "MET",
                    "CONTENT_COMPLETENESS": "MET",
                    "PEDAGOGICAL_QUALITY": "MET",
                    "VISUAL_PEDAGOGY": "MET",
                    "TERMINOLOGY_CONSISTENCY": "MET",
                    "SOURCE_TRACEABILITY": "MET",
                    "CLARITY_ORGANIZATION": "MET",
                    "FORMATTING": "MET",
                },
                "findings": [],
                "limitations": [],
            }),
        }

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=json.dumps(worker_env), stderr=""),
            MagicMock(returncode=0, stdout=json.dumps(auditor_env), stderr=""),
        ]

        res = controller.process_lesson("M01-L07", reset=True)
        self.assertEqual(res["status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(res["error_category"], "MODEL_NOT_VERIFIED_FOR_PASS")

    def test_real_mock_mode_switching_invalidates_incompatible_checkpoints(self):
        """22. Real/Mock mode switching invalidates incompatible checkpoints."""
        # 1. Run in mock mode -> MOCK_PASS
        mock_controller = CourseHarnessController(self.config_path, mode_override="mock")
        res_mock = mock_controller.process_lesson("M01-L07", reset=True)
        self.assertEqual(res_mock["status"], "MOCK_PASS")

        # 2. Switch to real automated_cli mode
        real_controller = CourseHarnessController(self.config_path, mode_override="automated_cli")
        real_controller.adapter.resolved_binary = "/bin/mock-agy"

        # Checkpoint cannot resume as PASS in real mode
        manifest = real_controller.get_manifest()
        src_sha = manifest["lessons"]["M01-L07"]["source_sha256"]
        self.assertFalse(real_controller.state_mgr.is_resumable_pass("M01-L07", src_sha))

        # Initializing lesson state in real mode resets the incompatible mock checkpoint
        chk = real_controller.state_mgr.initialize_lesson_state("M01-L07", src_sha, execution_mode="automated_cli")
        self.assertEqual(chk["status"], "PENDING")
        self.assertIsNone(chk.get("evidence_class"))

    def test_legacy_mock_pass_cannot_silently_become_production_pass(self):
        """23. Legacy MOCK PASS cannot silently become production PASS."""
        final_path, final_sha = self._create_final_file("M01-L07")
        audit_path, audit_sha = self._create_audit_report("M01-L07", final_sha, "legacy-mock-id")

        # Legacy checkpoint masquerading as PASS but with MOCK_SIMULATED evidence
        legacy_chk = {
            "lesson_id": "M01-L07",
            "status": "PASS",
            "source_sha256": "src_sha_test",
            "prompt_config_hash": "hash_v1",
            "final_path": final_path,
            "final_sha256": final_sha,
            "audit_path": audit_path,
            "audit_sha256": audit_sha,
            "audit_invocation_id": "legacy-mock-id",
            "evidence_class": "MOCK_SIMULATED",
            "history": [],
        }
        self.state_mgr.save_checkpoint("M01-L07", legacy_chk)

        # Resuming must fail closed and invalidate the checkpoint
        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L07", "src_sha_test"))
        updated_chk = self.state_mgr.load_checkpoint("M01-L07")
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertIn("UNVERIFIED_EVIDENCE_CLASS", updated_chk["error_category"])

    def test_human_accepted_remains_separate_and_validates_approval_artifact(self):
        """24. HUMAN_ACCEPTED remains separate and continues to validate its approval artifact correctly."""
        final_path, final_sha = self._create_final_file("M03-L08")

        chk = self.state_mgr.record_human_approval(
            lesson_id="M03-L08",
            reviewer="SME-Agile-Lead",
            approved_final_sha256=final_sha,
            notes="Explicit SME human acceptance",
        )
        self.assertEqual(chk["status"], "HUMAN_ACCEPTED")
        self.assertEqual(chk["verdict"], "HUMAN_ACCEPTED")
        self.assertEqual(chk["evidence_class"], "HUMAN_ACCEPTED")
        self.assertTrue(os.path.exists(chk["acceptance_path"]))
        self.assertTrue(self.state_mgr.is_resumable_pass("M03-L08", "src_sha_test"))


if __name__ == "__main__":
    unittest.main()
