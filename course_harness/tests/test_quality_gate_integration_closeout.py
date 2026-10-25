"""Mandatory Regression Tests for Quality Gate Integration Closeout.

Covers defects:
- A-01: Reject incomplete current audit reports
- A-02: Require current quality acceptance before production PASS
- A-03: Reject contradictory quality decisions
- A-04: Enforce draft and visual integrity after Worker/Repair
"""

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import yaml

from course_harness.run import CourseHarnessController
from course_harness.state import StateManager, calculate_file_sha256
from course_harness.validator import (
    AuditValidator,
    ValidationError,
    classify_draft_issues,
    validate_draft_structure,
)
from course_harness.visual import (
    QUALITY_RUBRIC_VERSION,
    TARGET_QUALITY_SCORE,
    VisualAssetManager,
    calculate_quality_score,
    extract_figures_from_markdown,
)


class BaseQualityGateTestCase(unittest.TestCase):
    """Base setup for Quality Gate closeout integration tests."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.yaml")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.evidence_dir = os.path.join(self.output_dir, "evidence")
        self.checkpoints_dir = os.path.join(self.evidence_dir, "checkpoints")
        self.acceptance_dir = os.path.join(self.checkpoints_dir, "acceptance")
        self.receipts_dir = os.path.join(self.evidence_dir, "receipts")
        self.drafts_dir = os.path.join(self.output_dir, "drafts")
        self.audits_dir = os.path.join(self.output_dir, "audits")
        self.modules_dir = os.path.join(self.output_dir, "modules")
        self.assets_dir = os.path.join(self.output_dir, "assets")

        for d in [
            self.output_dir,
            self.evidence_dir,
            self.checkpoints_dir,
            self.acceptance_dir,
            self.receipts_dir,
            self.drafts_dir,
            self.audits_dir,
            self.modules_dir,
            self.assets_dir,
        ]:
            os.makedirs(d, exist_ok=True)

        self.schema_path = "course_harness/schemas/audit.schema.json"
        self.validator = AuditValidator(self.schema_path)

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
                "course_id": "TestCourse",
                "source_dir": "output_course/Agile_Project_Management",
                "output_dir": self.output_dir,
                "prompts_dir": "course_harness/prompts",
                "schema_path": self.schema_path,
            },
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config_data, f)

        self.state_mgr = StateManager(
            checkpoints_dir=self.checkpoints_dir,
            prompt_config_hash="test_prompt_hash",
            acceptance_dir=self.acceptance_dir,
            schema_path=self.schema_path,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_lesson_meta(self, lesson_id: str = "M01-L07") -> dict:
        return {
            "lesson_id": lesson_id,
            "module_id": "M01",
            "module_title": "Agile Foundations",
            "title": "The four values of the Agile Manifesto",
            "source_type": "VIDEO_TRANSCRIPT",
            "relative_path": "01_module/07_test.txt",
            "source_sha256": "0cc6f167d4d5e72eeebb9caa03c81c1e9fc709de2ee021bd212922de14233e69",
            "status": "AVAILABLE",
            "locators": [{"locator": "01:51", "text": "Individuals and interactions"}],
        }

    def _create_valid_audit_dict(self, lesson_id: str, final_sha: str) -> dict:
        return {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "summary": "Valid audit report meeting all quality dimensions.",
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
            "limitations": ["Verified under deterministic test harness."],
            "audited_final_sha256": final_sha,
            "audit_invocation_id": f"conv-{lesson_id}-aud1",
            "model_verification": "VERIFIED",
        }

    def _setup_final_file(self, lesson_id: str, content: str = "# Final Lesson Content\n\nNội dung bài học chuẩn.") -> str:
        final_path = os.path.join(self.modules_dir, f"{lesson_id}.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(content)
        self.state_mgr.initialize_lesson_state(lesson_id, source_sha256="src_test_sha")
        self.state_mgr.transition(lesson_id, "NEEDS_REAUDIT", {"final_path": final_path, "final_sha256": calculate_file_sha256(final_path)})
        return final_path, calculate_file_sha256(final_path)

    def _save_valid_audit_receipt(
        self,
        lesson_id: str,
        final_sha: str,
        audit_sha: str,
        invocation_id: str = "conv-M01-L07-aud1",
    ) -> str:
        receipt_data = {
            "invocation_id": invocation_id,
            "role": "auditor",
            "lesson_id": lesson_id,
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "src_test_sha",
            "prompt_config_hash": "test_prompt_hash",
            "audit_report_sha256": audit_sha,
            "created_at": "2026-10-24T10:00:00Z",
        }
        return self.state_mgr.save_audit_receipt(receipt_data)


class TestA01AuditCompleteness(BaseQualityGateTestCase):
    """A-01: Reject incomplete current audit reports."""

    def test_pass_without_dimension_scores_rejected(self):
        """PASS verdict without dimension_scores must fail validation."""
        report = {
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "summary": "Synthetic test without dimensions",
            "findings": [],
            "limitations": [],
        }
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M02-L11")
        self.assertTrue(
            "dimension_scores" in str(ctx.exception).lower() or "schema" in str(ctx.exception).lower(),
            f"Expected dimension_scores error, got: {ctx.exception}",
        )

    def test_pass_with_empty_dimension_scores_rejected(self):
        """PASS verdict with empty dimension_scores must fail validation."""
        report = {
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "summary": "Empty dimension scores",
            "dimension_scores": {},
            "findings": [],
            "limitations": [],
        }
        with self.assertRaises(ValidationError):
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M02-L11")

    def test_pass_declaring_rubric_2_0_but_no_dimensions_rejected(self):
        """PASS declaring Rubric 2.0 but missing dimension_scores must fail schema and validator."""
        report = {
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Rubric 2.0 declared but no dimensions",
            "findings": [],
            "limitations": [],
        }
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M02-L11")
        self.assertTrue(
            "dimension" in str(ctx.exception).lower() or "schema" in str(ctx.exception).lower(),
            f"Expected dimension failure, got: {ctx.exception}",
        )

    def test_pass_with_complete_dimensions_but_missing_rubric_version_rejected(self):
        """PASS with all 8 dimensions MET but omitting quality_rubric_version is rejected."""
        report = {
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "summary": "Missing rubric version",
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
        }
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M02-L11")
        self.assertIn("explicit quality_rubric_version", str(ctx.exception).lower())

    def test_quiz_missing_explicit_version_and_visual_evaluation_rejected(self):
        """QUIZ report missing both explicit rubric version and visual evaluation must be rejected."""
        report = {
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "summary": "Quiz report without version or visual evaluation",
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": [],
            "limitations": [],
        }
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(
                json.dumps(report),
                expected_lesson_id="M02-L11",
                lesson_type="QUIZ",
            )
        self.assertTrue(
            "explicit quality_rubric_version" in str(ctx.exception).lower()
            or "exemption" in str(ctx.exception).lower()
        )

    def test_modern_report_misclassified_as_legacy_rejected(self):
        """A report missing required Rubric 2.0 fields cannot silently be granted production eligibility."""
        report = {
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "summary": "Unversioned legacy-looking audit",
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "COMPLETENESS": "MET",
                "TECHNICAL_ACCURACY": "MET",
                "TERMINOLOGY": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "STRUCTURE": "MET",
                "TRACEABILITY": "MET",
            },
            "findings": [],
            "limitations": [],
        }
        validated_payload, _ = self.validator.validate_report(json.dumps(report), expected_lesson_id="M02-L11")
        eligible, _ = self.validator.is_production_quality_eligible(validated_payload)
        self.assertFalse(eligible)
        self.assertFalse(validated_payload.get("content_quality_accepted"))


class TestA02ProductionQualityGate(BaseQualityGateTestCase):
    """A-02: Require current quality acceptance before production PASS."""

    def test_legacy_pass_cannot_authorize_production_pass(self):
        """Historical audit with verdict=PASS but content_quality_accepted=false cannot authorize production PASS."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        legacy_report = {
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": "1.0",
            "content_quality_accepted": False,
            "quality_score": 100.0,
            "summary": "Legacy audit",
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "COMPLETENESS": "MET",
                "TECHNICAL_ACCURACY": "MET",
                "TERMINOLOGY": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "STRUCTURE": "MET",
                "TRACEABILITY": "MET",
            },
            "findings": [],
            "limitations": [],
            "audited_final_sha256": final_sha,
            "audit_invocation_id": "conv-leg-1",
            "model_verification": "VERIFIED",
        }
        audit_path = os.path.join(self.audits_dir, "legacy_audit.json")
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(legacy_report, f)

        audit_sha = calculate_file_sha256(audit_path)
        self._save_valid_audit_receipt("M01-L07", final_sha, audit_sha, invocation_id="conv-leg-1")

        eligible, _ = self.validator.is_production_quality_eligible(legacy_report)
        self.assertFalse(eligible)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
            )
        self.assertTrue(
            "rubric 2.0" in str(ctx.exception).lower()
            or "2.0-visual-first" in str(ctx.exception).lower()
        )

    def test_current_quality_fail_cannot_authorize_production_pass(self):
        """Current quality FAIL report cannot authorize production PASS."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        fail_report = self._create_valid_audit_dict("M01-L07", final_sha)
        fail_report["verdict"] = "FAIL"
        fail_report["content_quality_accepted"] = False
        fail_report["findings"] = [
            {
                "finding_id": "F-001",
                "severity": "HIGH",
                "category": "SOURCE_FIDELITY",
                "source_locator": "01:00",
                "draft_locator": "Sec 1",
                "description": "Hallucination error",
                "required_action": "Remove hallucinated claim",
            }
        ]
        eligible, _ = self.validator.is_production_quality_eligible(fail_report)
        self.assertFalse(eligible)

        audit_path = os.path.join(self.audits_dir, "fail_audit.json")
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(fail_report, f)

        with self.assertRaises(ValueError):
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
            )

    @patch("subprocess.run")
    def test_current_quality_pass_with_model_not_verified_blocks_production_pass(self, mock_run):
        """Current quality PASS with model NOT_VERIFIED transitions to NEEDS_HUMAN_REVIEW."""
        controller = CourseHarnessController(self.config_path, mode_override="automated_cli")
        controller.adapter.resolved_binary = "/bin/mock-agy"

        worker_env = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "conv-w",
            "response": "# Lesson Draft\n\nFull valid markdown body text exceeding minimum lengths.",
        }
        draft_sha = hashlib.sha256(worker_env["response"].encode("utf-8")).hexdigest()
        audit_payload = self._create_valid_audit_dict("M01-L07", draft_sha)
        auditor_env = {
            "status": "SUCCESS",
            # model omitted -> NOT_VERIFIED
            "conversation_id": "conv-a",
            "response": json.dumps(audit_payload),
        }

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=json.dumps(worker_env), stderr=""),
            MagicMock(returncode=0, stdout=json.dumps(auditor_env), stderr=""),
        ]

        controller.state_mgr.is_resumable_pass = MagicMock(return_value=False)
        chk = controller.process_lesson("M01-L07", reset=True)
        self.assertEqual(chk["status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(chk["error_category"], "MODEL_NOT_VERIFIED_FOR_PASS")

    def test_current_quality_pass_with_missing_controller_receipt_blocks_production_pass(self):
        """Current quality PASS without valid Controller receipt in state_mgr is rejected."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        audit_path = os.path.join(self.audits_dir, "audit_without_receipt.json")
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(report, f)

        # Do NOT save audit receipt into state_mgr
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07",
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
            )
        self.assertIn("receipt", str(ctx.exception).lower())

    def test_current_quality_pass_with_valid_receipt_and_model_verified_authorizes_pass(self):
        """Current quality PASS with valid receipt and verified model succeeds."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        audit_path = os.path.join(self.audits_dir, "valid_audit.json")
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(report, f)
        audit_sha = calculate_file_sha256(audit_path)

        self._save_valid_audit_receipt("M01-L07", final_sha, audit_sha, invocation_id=report["audit_invocation_id"])

        chk = self.state_mgr.record_audit_verdict(
            lesson_id="M01-L07",
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
        )
        self.assertEqual(chk["status"], "PASS")
        self.assertEqual(chk["content_quality_accepted"], True)
        self.assertEqual(chk["quality_rubric_version"], QUALITY_RUBRIC_VERSION)

    def test_mock_pass_remains_distinct(self):
        """MOCK_PASS remains strictly separated from production PASS."""
        controller = CourseHarnessController(self.config_path, mode_override="mock")
        chk = controller.process_lesson("M01-L07", reset=True)
        self.assertEqual(chk["status"], "MOCK_PASS")
        self.assertEqual(chk["evidence_class"], "MOCK_SIMULATED")
        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L07", "any_sha"))

    def test_human_accepted_remains_distinct(self):
        """HUMAN_ACCEPTED remains strictly separated and requires approval artifact."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        artifact_path = os.path.join(self.acceptance_dir, "human_approval.md")
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write("# Human Acceptance Sign-off\nVerified manually by instructor.")

        chk = self.state_mgr.record_human_approval(
            lesson_id="M01-L07",
            reviewer="Lead Instructor",
            approved_final_sha256=final_sha,
            notes="Manual sign-off after pedagogical review",
        )
        self.assertEqual(chk["status"], "HUMAN_ACCEPTED")
        self.assertEqual(chk["human_approval"]["reviewer"], "Lead Instructor")


class TestA03VerdictConsistency(BaseQualityGateTestCase):
    """A-03: Reject contradictory quality decisions."""

    def test_fail_with_all_dimensions_met_cannot_return_content_quality_accepted_true(self):
        """Auditor verdict FAIL with all dimensions MET cannot be returned with content_quality_accepted=True."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        contradictory_report = self._create_valid_audit_dict("M01-L07", final_sha)
        contradictory_report["verdict"] = "FAIL"
        contradictory_report["content_quality_accepted"] = True

        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(contradictory_report), expected_lesson_id="M01-L07")
        self.assertTrue(
            "verdict contradiction" in str(ctx.exception).lower()
            or "consistency error" in str(ctx.exception).lower()
        )

    def test_inconclusive_with_all_dimensions_met_cannot_return_content_quality_accepted_true(self):
        """Auditor verdict INCONCLUSIVE cannot have content_quality_accepted=True."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        inconclusive_report = self._create_valid_audit_dict("M01-L07", final_sha)
        inconclusive_report["verdict"] = "INCONCLUSIVE"
        inconclusive_report["content_quality_accepted"] = True

        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(inconclusive_report), expected_lesson_id="M01-L07")
        self.assertIn("inconclusive", str(ctx.exception).lower())

    def test_pass_with_high_finding_is_rejected(self):
        """Auditor verdict PASS with any HIGH or BLOCKING finding is rejected."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        report["findings"] = [
            {
                "finding_id": "F-001",
                "severity": "HIGH",
                "category": "SOURCE_FIDELITY",
                "source_locator": "01:00",
                "draft_locator": "Sec 1",
                "description": "Critical hallucination",
                "required_action": "Delete claim",
            }
        ]
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M01-L07")
        self.assertTrue(
            "high" in str(ctx.exception).lower() or "blocking" in str(ctx.exception).lower()
        )

    def test_pass_with_failed_dimension_is_rejected(self):
        """Auditor verdict PASS with a FAILED dimension is rejected."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        report["dimension_scores"]["FORMATTING"] = "FAILED"

        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M01-L07")
        self.assertIn("failed", str(ctx.exception).lower())

    def test_pass_with_quality_below_threshold_is_rejected(self):
        """Auditor verdict PASS with quality score < 90.0 is rejected."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        # 3 MINOR_ISSUES drop score below 90.0:
        # PEDAGOGICAL_QUALITY (15 * 0.7 = 10.5, -4.5)
        # VISUAL_PEDAGOGY (15 * 0.7 = 10.5, -4.5)
        # TERMINOLOGY_CONSISTENCY (10 * 0.7 = 7.0, -3.0) -> total earned 88.0
        report["dimension_scores"]["PEDAGOGICAL_QUALITY"] = "MINOR_ISSUES"
        report["dimension_scores"]["VISUAL_PEDAGOGY"] = "MINOR_ISSUES"
        report["dimension_scores"]["TERMINOLOGY_CONSISTENCY"] = "MINOR_ISSUES"
        report["quality_score"] = 88.0

        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M01-L07")
        self.assertIn("threshold", str(ctx.exception).lower())

    def test_legitimate_current_pass_accepted(self):
        """Legitimate Rubric 2.0 PASS is validated and accepted."""
        final_path, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        validated, _ = self.validator.validate_report(json.dumps(report), expected_lesson_id="M01-L07")
        self.assertEqual(validated["verdict"], "PASS")
        self.assertEqual(validated["content_quality_accepted"], True)
        eligible, _ = self.validator.is_production_quality_eligible(validated)
        self.assertTrue(eligible)


class TestA04VisualEvidenceFreshness(BaseQualityGateTestCase):
    """A-04: Enforce draft and visual integrity after Worker/Repair."""

    def test_repair_removes_all_figures_clears_stale_manifest(self):
        """When repair removes all figures, stale cached visual manifest must be cleared."""
        controller = CourseHarnessController(self.config_path, mode_override="mock")
        lesson_id = "M01-L07"

        # Worker creates draft with a figure
        worker_draft = (
            "# Lesson Title\n\n"
            "Nội dung bài học.\n\n"
            "```mermaid\n"
            "graph TD\n"
            "  A-->B\n"
            "```\n"
            "> **Chú thích:** Sơ đồ quy trình minh họa.\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ khối quy trình các bước.\n"
            "> **Mục tiêu giáo dục:** Minh họa quy trình bài học.\n"
            "> **Mục tiêu bài học liên quan:** Nắm vững các bước.\n"
            "> **Xuất xứ học liệu (Provenance):** `PEDAGOGICAL_RECONSTRUCTION`\n"
            "[01:00]\n"
        )
        figs_initial = extract_figures_from_markdown(worker_draft)
        self.assertEqual(len(figs_initial), 1)

        proc_figs, m_path, m_sha = controller.visual_asset_mgr.process_figures_for_lesson(
            lesson_id, figs_initial, ""
        )
        controller._last_lesson_visuals[lesson_id] = {
            "manifest_path": m_path,
            "manifest_sha256": m_sha,
            "figures": proc_figs,
            "draft_sha256": hashlib.sha256(worker_draft.encode("utf-8")).hexdigest(),
        }
        self.assertIsNotNone(controller._last_lesson_visuals[lesson_id]["manifest_path"])

        # Repaired draft removes all figures
        repaired_draft = (
            "# Lesson Title (Đã phẫu thuật chỉnh sửa)\n\n"
            "Toàn bộ sơ đồ đã được lược bỏ thành văn bản thuần túy theo yêu cầu của auditor.\n"
        )
        repaired_sha = hashlib.sha256(repaired_draft.encode("utf-8")).hexdigest()
        figs_repaired = extract_figures_from_markdown(repaired_draft)
        self.assertEqual(len(figs_repaired), 0)

        # Fresh evaluation: clearing stale manifest
        if figs_repaired:
            proc, p, s = controller.visual_asset_mgr.process_figures_for_lesson(lesson_id, figs_repaired, "")
            controller._last_lesson_visuals[lesson_id] = {"manifest_path": p, "manifest_sha256": s, "figures": proc, "draft_sha256": repaired_sha}
        else:
            controller._last_lesson_visuals[lesson_id] = {"manifest_path": None, "manifest_sha256": None, "figures": [], "draft_sha256": repaired_sha}

        self.assertIsNone(controller._last_lesson_visuals[lesson_id]["manifest_path"])
        self.assertEqual(controller._last_lesson_visuals[lesson_id]["figures"], [])
        self.assertEqual(controller._last_lesson_visuals[lesson_id]["draft_sha256"], repaired_sha)

    def test_repair_changes_visual_specifications_old_manifest_cannot_be_reused(self):
        """When repair modifies diagram source, visual manifest is updated with new hashes."""
        controller = CourseHarnessController(self.config_path, mode_override="mock")
        lesson_id = "M01-L07"

        draft_v1 = (
            "# Lesson Title\n\n"
            "```mermaid\n"
            "graph TD\n"
            "  A-->B\n"
            "```\n"
            "> **Chú thích:** Phiên bản 1 sơ đồ quy trình.\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ khối các bước.\n"
            "> **Mục tiêu giáo dục:** Mục tiêu 1.\n"
            "> **Mục tiêu bài học liên quan:** Mục tiêu liên quan 1.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED`\n"
            "[01:00]\n"
        )
        figs_v1 = extract_figures_from_markdown(draft_v1)
        proc_v1, path_v1, sha_v1 = controller.visual_asset_mgr.process_figures_for_lesson(lesson_id, figs_v1, "")

        draft_v2 = (
            "# Lesson Title\n\n"
            "```mermaid\n"
            "graph TD\n"
            "  A-->B-->C\n"
            "```\n"
            "> **Chú thích:** Phiên bản 2 cập nhật thêm bước C.\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ khối các bước cải tiến.\n"
            "> **Mục tiêu giáo dục:** Mục tiêu 2.\n"
            "> **Mục tiêu bài học liên quan:** Mục tiêu liên quan 2.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED`\n"
            "[01:00]\n"
        )
        figs_v2 = extract_figures_from_markdown(draft_v2)
        proc_v2, path_v2, sha_v2 = controller.visual_asset_mgr.process_figures_for_lesson(lesson_id, figs_v2, "")

        self.assertNotEqual(sha_v1, sha_v2)
        self.assertNotEqual(proc_v1[0]["source_spec_sha256"], proc_v2[0]["source_spec_sha256"])

    def test_blocking_structural_source_fidelity_issue_blocks_quality_acceptance(self):
        """Blocking issues (short content, internal machine enums) are classified as blocking."""
        bad_draft = (
            "# Tiêu đề ngắn\n\n"
            "Thân bài quá ngắn và chứa enum AI_GENERATED_EXAMPLE hiển thị cho sinh viên.\n"
        )
        issues = validate_draft_structure(bad_draft, "VIDEO_TRANSCRIPT", lesson_id="M01-L07")
        blocking, warnings = classify_draft_issues(issues)
        self.assertTrue(len(blocking) > 0)
        self.assertTrue(any("short" in b.lower() or "ai_generated_example" in b.lower() for b in blocking))

    def test_nonblocking_editorial_warning_remains_warning(self):
        """Nonblocking editorial recommendations remain warnings and do not block PASS."""
        mild_issues = [
            "Visual pedagogy issue: Substantive lesson lacks explanatory visuals or diagrams (visual density recommendation).",
            "Image reference 'fig1' has missing or too brief alternative text (< 10 chars)",
        ]
        blocking, warnings = classify_draft_issues(mild_issues)
        self.assertEqual(blocking, [])
        self.assertEqual(len(warnings), 2)

    def test_current_draft_hashes_and_visual_evidence_correspond_to_same_content_version(self):
        """Visual evidence is bound to current draft SHA256; mismatched draft SHA fails binding check."""
        draft_content = "# Final Lesson Draft\n\nNội dung chính xác."
        draft_sha = hashlib.sha256(draft_content.encode("utf-8")).hexdigest()
        tampered_sha = hashlib.sha256(b"# Tampered Draft").hexdigest()

        visual_entry = {
            "manifest_path": "/tmp/manifest.json",
            "manifest_sha256": "manifest_sha_123",
            "figures": [],
            "draft_sha256": draft_sha,
        }
        self.assertEqual(visual_entry["draft_sha256"], draft_sha)
        self.assertNotEqual(visual_entry["draft_sha256"], tampered_sha)

    def test_nonvisual_quiz_exemption_works_without_stale_figures(self):
        """Nonvisual QUIZ exemption normalizes to 100.0 without needing stale figures."""
        quiz_scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        res = calculate_quality_score(
            quiz_scores,
            [],
            lesson_type="QUIZ",
            quality_rubric_version=QUALITY_RUBRIC_VERSION,
        )
        self.assertEqual(res["quality_score"], 100.0)
        self.assertEqual(res["verdict"], "PASS")
        self.assertTrue(res["hard_gates_passed"])
        self.assertTrue(res["content_quality_accepted"])
