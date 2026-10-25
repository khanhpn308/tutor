"""Comprehensive Acceptance Tests for R2 Hotfix findings (R2-B01, R2-B02, R2-B03, R2-B04).

Covers:
- R2-B01: Unified AGY JSON transport envelope validation on production call paths
- R2-B02: Authoritative audit report verdict validation & content binding
- R2-B03: Human acceptance state (HUMAN_ACCEPTED), artifact integrity, and resume semantics
- R2-B04: Fail-closed model verification policy across Worker, Auditor, and Repair
- Small consistency fixes: bulk pilot execution guard and fidelity hazard scoping
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

import yaml

from course_harness.cli_adapter import (
    AgyAdapter,
    CliExecutionError,
    ModelUnavailableError,
)
from course_harness.run import CourseHarnessController, main
from course_harness.state import StateManager, calculate_file_sha256
from course_harness.validator import (
    AuditValidator,
    ValidationError,
    validate_draft_structure,
    validate_source_fidelity_numerical_claims,
)


class BaseR2TestCase(unittest.TestCase):
    """Base test case setting up temp directories, minimal configs, and mock helpers."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.yaml")
        self.output_dir = os.path.join(self.test_dir, "generated")
        self.evidence_dir = os.path.join(self.output_dir, "evidence")
        self.checkpoints_dir = os.path.join(self.evidence_dir, "checkpoints")
        self.acceptance_dir = os.path.join(self.checkpoints_dir, "acceptance")
        self.drafts_dir = os.path.join(self.output_dir, "drafts")
        self.audits_dir = os.path.join(self.output_dir, "audits")
        self.modules_dir = os.path.join(self.output_dir, "modules")

        for d in [
            self.output_dir,
            self.evidence_dir,
            self.checkpoints_dir,
            self.acceptance_dir,
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
            "relative_path": "01_module-1-agile-project-management/01_course-introduction/07_the-four-values-of-the-agile-manifesto.txt",
            "source_sha256": "0cc6f167d4d5e72eeebb9caa03c81c1e9fc709de2ee021bd212922de14233e69",
            "status": "AVAILABLE",
            "locators": [{"locator": "01:51", "text": "Individuals and interactions"}],
        }

    def _create_valid_audit_dict(self, lesson_id: str, final_sha: str) -> dict:
        return {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
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

    def _save_valid_audit_receipt(
        self,
        lesson_id: str,
        final_sha: str,
        audit_sha: str,
        invocation_id: str = "conv-M01-L07-aud1",
        source_sha256: str = "src_sha_test",
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
            "source_sha256": source_sha256,
            "prompt_config_hash": "hash_v1",
            "audit_report_sha256": audit_sha,
            "created_at": "2026-10-23T10:00:00Z",
        }
        return self.state_mgr.save_audit_receipt(receipt_data)


class TestR2B01UnifiedAgyEnvelope(BaseR2TestCase):
    """R2-B01: Unified AGY JSON transport envelope validation on production call paths."""

    def setUp(self):
        super().setUp()
        self.controller = CourseHarnessController(self.config_path, mode_override="automated_cli")
        self.controller.adapter.resolved_binary = "/bin/mock-agy"

    @patch("subprocess.run")
    def test_worker_production_callpath_valid_envelope_markdown_only(self, mock_run):
        """Worker parses valid AGY envelope and returns/saves clean Markdown only (not transport JSON)."""
        valid_markdown = (
            "# Bài học M01-L07: Bốn giá trị cốt lõi\n\n"
            "## 1. Mục tiêu bài học (Learning Objectives)\n- Hiểu rõ 4 giá trị Agile.\n\n"
            "## 2. Kiến thức nền tảng (Context)\n- Lịch sử Tuyên ngôn Agile 2001.\n\n"
            "## 3. Nội dung lý thuyết trọng tâm (Theory)\n- Cá nhân và tương tác hơn quy trình và công cụ.\n\n"
            "## 5. Bảng thuật ngữ chuyên ngành Anh - Việt\n| Term | Nghĩa | Ghi chú |\n| Agile | Linh hoạt | Phương pháp |\n\n"
            "## 6. Tóm tắt cốt lõi (Key Takeaways)\n- Ưu tiên vế trái hơn vế phải.\n\n"
            "## 8. Nguồn đối chiếu (Source Traceability)\n- Timestamp [01:51].\n"
        )
        envelope = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "worker-conv-123",
            "response": valid_markdown,
            "usage": {"total_tokens": 500},
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(envelope), stderr="")

        lesson_meta = self._create_mock_lesson_meta("M01-L07")
        clean_text, draft_path, meta = self.controller._run_worker_draft(lesson_meta, "Raw source content")

        # Verify returned content is Markdown only
        self.assertEqual(clean_text, valid_markdown.strip())
        self.assertNotIn('"status": "SUCCESS"', clean_text)
        self.assertNotIn('"conversation_id"', clean_text)
        self.assertEqual(meta["model_verified"], "VERIFIED")

        # Verify file on disk is Markdown only
        with open(draft_path, "r", encoding="utf-8") as f:
            disk_content = f.read()
        self.assertEqual(disk_content, valid_markdown.strip())
        self.assertFalse(disk_content.strip().startswith("{"))

    @patch("subprocess.run")
    def test_auditor_production_callpath_valid_envelope_audit_json(self, mock_run):
        """Auditor parses valid envelope and returns validated audit report dict."""
        draft_content = "# Sample draft content for audit verification"
        draft_sha = hashlib.sha256(draft_content.encode("utf-8")).hexdigest()
        audit_payload = self._create_valid_audit_dict("M01-L07", draft_sha)

        envelope = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "auditor-conv-456",
            "response": json.dumps(audit_payload),
            "usage": {"total_tokens": 700},
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(envelope), stderr="")

        lesson_meta = self._create_mock_lesson_meta("M01-L07")
        report, audit_path, meta = self.controller._run_auditor(lesson_meta, "Raw source", draft_content, attempt=1)

        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["audited_final_sha256"], draft_sha)
        self.assertEqual(report["audit_invocation_id"], meta["invocation_id"])
        self.assertEqual(meta["conversation_id"], "auditor-conv-456")
        self.assertTrue(report["audit_invocation_id"].startswith("inv-auditor-M01-L07-att1-"))
        self.assertEqual(meta["model_verified"], "VERIFIED")
        self.assertTrue(os.path.exists(audit_path))
        # Receipt was persisted by controller
        receipt = self.controller.state_mgr.get_audit_receipt(report["audit_invocation_id"])
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt["audited_final_sha256"], draft_sha)

    @patch("subprocess.run")
    def test_repair_production_callpath_valid_envelope_markdown_only(self, mock_run):
        """Repair parses valid envelope and returns repaired Markdown only."""
        repaired_markdown = (
            "# Bài học M01-L07 (Đã phẫu thuật chỉnh sửa)\n\n"
            "## 1. Mục tiêu bài học (Learning Objectives)\n- Đã sửa theo findings.\n"
        )
        envelope = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "repair-conv-789",
            "response": repaired_markdown,
            "usage": {"total_tokens": 400},
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(envelope), stderr="")

        lesson_meta = self._create_mock_lesson_meta("M01-L07")
        repaired_text, repaired_path, meta = self.controller._run_repair(
            lesson_meta, "Raw source", "Old draft", [], attempt=1
        )

        self.assertEqual(repaired_text, repaired_markdown.strip())
        self.assertNotIn('"status": "SUCCESS"', repaired_text)
        with open(repaired_path, "r", encoding="utf-8") as f:
            disk_content = f.read()
        self.assertEqual(disk_content, repaired_markdown.strip())

    @patch("subprocess.run")
    def test_failed_status_blocks_all_three_roles(self, mock_run):
        """Non-terminal or failed status in envelope blocks Worker, Auditor, and Repair."""
        for bad_status in ["ERROR", "FAILED", "WAITING", "INTERRUPTED", "CANCELLED", "TIMEOUT"]:
            failed_envelope = {"status": bad_status, "response": "Incomplete text"}
            mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(failed_envelope), stderr="")
            lesson_meta = self._create_mock_lesson_meta("M01-L07")

            with self.assertRaises(CliExecutionError) as ctx:
                self.controller._run_worker_draft(lesson_meta, "Raw content")
            self.assertIn("non-terminal", str(ctx.exception).lower())

            with self.assertRaises(CliExecutionError) as ctx:
                self.controller._run_auditor(lesson_meta, "Raw content", "Draft content", attempt=1)
            self.assertIn("non-terminal", str(ctx.exception).lower())

            with self.assertRaises(CliExecutionError) as ctx:
                self.controller._run_repair(lesson_meta, "Raw content", "Draft content", [], attempt=1)
            self.assertIn("non-terminal", str(ctx.exception).lower())

    @patch("subprocess.run")
    def test_malformed_envelope_blocks_all_three_roles(self, mock_run):
        """Malformed/non-JSON output from CLI blocks Worker, Auditor, and Repair."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Fatal: segfault in agy binary\nNon-json text", stderr=""
        )
        lesson_meta = self._create_mock_lesson_meta("M01-L07")

        with self.assertRaises(CliExecutionError) as ctx:
            self.controller._run_worker_draft(lesson_meta, "Raw")
        self.assertIn("MALFORMED_AGY_JSON", str(ctx.exception))

        with self.assertRaises(CliExecutionError) as ctx:
            self.controller._run_auditor(lesson_meta, "Raw", "Draft", 1)
        self.assertIn("MALFORMED_AGY_JSON", str(ctx.exception))

        with self.assertRaises(CliExecutionError) as ctx:
            self.controller._run_repair(lesson_meta, "Raw", "Draft", [], 1)
        self.assertIn("MALFORMED_AGY_JSON", str(ctx.exception))

    @patch("subprocess.run")
    def test_missing_or_empty_response_rejected(self, mock_run):
        """Envelope with missing or whitespace-only response field is rejected."""
        empty_env = {"status": "SUCCESS", "model": "gemini-3.8-flash-high", "response": "   "}
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(empty_env), stderr="")
        lesson_meta = self._create_mock_lesson_meta("M01-L07")

        with self.assertRaises(CliExecutionError) as ctx:
            self.controller._run_worker_draft(lesson_meta, "Raw")
        self.assertIn("Empty 'response' text", str(ctx.exception))

    @patch("subprocess.run")
    def test_model_mismatch_rejected(self, mock_run):
        """If AGY reports a different fallback model, ModelUnavailableError is raised."""
        mismatch_env = {
            "status": "SUCCESS",
            "model": "gemini-1.5-pro",
            "response": "# Output from wrong model",
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mismatch_env), stderr="")
        lesson_meta = self._create_mock_lesson_meta("M01-L07")

        with self.assertRaises(ModelUnavailableError) as ctx:
            self.controller._run_worker_draft(lesson_meta, "Raw")
        self.assertIn("model mismatch", str(ctx.exception).lower())

    @patch("subprocess.run")
    def test_json_transport_never_written_as_lesson_content(self, mock_run):
        """If model leaks raw transport JSON into response, draft saving is blocked."""
        leaked_env = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "response": json.dumps({"status": "SUCCESS", "response": "nested leaked text"}),
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(leaked_env), stderr="")
        lesson_meta = self._create_mock_lesson_meta("M01-L07")

        with self.assertRaises(CliExecutionError) as ctx:
            self.controller._run_worker_draft(lesson_meta, "Raw")
        self.assertIn("LEAKED_TRANSPORT_JSON", str(ctx.exception))


class TestR2B02SecureAuditVerdict(BaseR2TestCase):
    """R2-B02: Secure Audit Verdict Recording and provenance binding."""

    def _setup_final_file(self, lesson_id: str, content: str = "# Final Content") -> tuple:
        final_path = os.path.join(self.modules_dir, f"{lesson_id}_final.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(content)
        sha = calculate_file_sha256(final_path)
        self.state_mgr.initialize_lesson_state(lesson_id, source_sha256="src_sha_test")
        self.state_mgr.transition(lesson_id, "NEEDS_REAUDIT", {"final_path": final_path, "final_sha256": sha})
        return final_path, sha

    def _write_audit_file(self, lesson_id: str, payload: dict) -> str:
        audit_path = os.path.join(self.audits_dir, f"{lesson_id}_audit_test.json")
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return audit_path

    def test_valid_source_bound_pass_audit_accepted(self):
        """Valid source-bound PASS audit with matching SHA256 and invocation evidence is accepted."""
        _, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        audit_path = self._write_audit_file("M01-L07", report)
        audit_sha = calculate_file_sha256(audit_path)
        self._save_valid_audit_receipt("M01-L07", final_sha, audit_sha, invocation_id=report["audit_invocation_id"])

        chk = self.state_mgr.record_audit_verdict(
            lesson_id="M01-L07",
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            notes="Audit verified valid.",
        )
        self.assertEqual(chk["status"], "PASS")
        self.assertEqual(chk["verdict"], "PASS")
        self.assertEqual(chk["final_sha256"], final_sha)
        self.assertTrue(self.state_mgr.is_resumable_pass("M01-L07", "src_sha_test"))

    def test_schema_invalid_audit_rejected(self):
        """Audit JSON that violates audit.schema.json must be rejected."""
        _, final_sha = self._setup_final_file("M01-L07")
        bad_report = {
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            # missing summary, findings, limitations
            "audited_final_sha256": final_sha,
        }
        audit_path = self._write_audit_file("M01-L07", bad_report)

        with self.assertRaises(ValidationError):
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07", verdict="PASS", audit_path=audit_path, expected_final_sha256=final_sha
            )

    def test_audit_report_fail_caller_pass_rejected(self):
        """If audit report verdict is FAIL while caller requests PASS, recording is rejected."""
        _, final_sha = self._setup_final_file("M01-L07")
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
                "description": "Hallucination",
                "required_action": "Fix it",
            }
        ]
        audit_path = self._write_audit_file("M01-L07", fail_report)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07", verdict="PASS", audit_path=audit_path, expected_final_sha256=final_sha
            )
        self.assertIn("verdict rejected", str(ctx.exception).lower())

    def test_wrong_lesson_id_rejected(self):
        """Audit report declaring a different lesson_id than the target lesson must be rejected."""
        _, final_sha = self._setup_final_file("M01-L07")
        wrong_id_report = self._create_valid_audit_dict("M02-L11", final_sha)
        audit_path = self._write_audit_file("M01-L07", wrong_id_report)

        with self.assertRaises(ValidationError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07", verdict="PASS", audit_path=audit_path, expected_final_sha256=final_sha
            )
        self.assertIn("Lesson ID mismatch", str(ctx.exception))

    def test_missing_audited_final_hash_rejected(self):
        """Audit report missing audited_final_sha256 field cannot grant PASS."""
        _, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        del report["audited_final_sha256"]
        audit_path = self._write_audit_file("M01-L07", report)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07", verdict="PASS", audit_path=audit_path, expected_final_sha256=final_sha
            )
        self.assertIn("lacks 'audited_final_sha256' binding", str(ctx.exception))

    def test_mismatched_final_sha_rejected(self):
        """Audit report bound to a different content SHA256 must be rejected."""
        _, final_sha = self._setup_final_file("M01-L07")
        mismatched_report = self._create_valid_audit_dict("M01-L07", "a" * 64)
        audit_path = self._write_audit_file("M01-L07", mismatched_report)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07", verdict="PASS", audit_path=audit_path, expected_final_sha256=final_sha
            )
        self.assertIn("does not match disk final SHA256", str(ctx.exception))

    def test_reusing_old_m03_l08_audit_for_corrected_final_rejected(self):
        """Reusing historical M03-L08 audit_v1.json to approve the corrected final lesson must be rejected."""
        corrected_content = "# Corrected M03-L08 Content without 70% mortality claim"
        _, final_sha = self._setup_final_file("M03-L08", content=corrected_content)

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
        self.assertIn("lacks 'audited_final_sha256' binding", str(ctx.exception))

    def test_high_or_blocking_findings_rejected(self):
        """Audit report claiming PASS but containing HIGH or BLOCKING findings must be rejected."""
        _, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        report["findings"] = [
            {
                "finding_id": "F-BLOCK-1",
                "severity": "BLOCKING",
                "category": "TECHNICAL_ACCURACY",
                "source_locator": "01:00",
                "draft_locator": "Section 2",
                "description": "Critical flaw",
                "required_action": "Rewrite",
            }
        ]
        audit_path = self._write_audit_file("M01-L07", report)

        with self.assertRaises(ValidationError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07", verdict="PASS", audit_path=audit_path, expected_final_sha256=final_sha
            )
        self.assertIn("blocking finding", str(ctx.exception).lower())

    def test_failed_dimension_rejected(self):
        """Audit report claiming PASS but having a FAILED dimension score must be rejected."""
        _, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        report["dimension_scores"]["SOURCE_FIDELITY"] = "FAILED"
        audit_path = self._write_audit_file("M01-L07", report)

        with self.assertRaises(ValidationError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07", verdict="PASS", audit_path=audit_path, expected_final_sha256=final_sha
            )
        self.assertIn("scored 'FAILED'", str(ctx.exception))

    def test_missing_actual_invocation_evidence_rejected(self):
        """Audit report lacking invocation evidence cannot grant verified AI PASS."""
        _, final_sha = self._setup_final_file("M01-L07")
        report = self._create_valid_audit_dict("M01-L07", final_sha)
        del report["audit_invocation_id"]
        audit_path = self._write_audit_file("M01-L07", report)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L07", verdict="PASS", audit_path=audit_path, expected_final_sha256=final_sha
            )
        self.assertIn("Missing actual invocation evidence", str(ctx.exception))


class TestR2B03HumanAcceptance(BaseR2TestCase):
    """R2-B03: Human acceptance artifact, durable state, and resume consistency."""

    def _setup_final_file(self, lesson_id: str = "M03-L08") -> tuple:
        final_path = os.path.join(self.modules_dir, f"{lesson_id}_final.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write("# Final Lesson Subject to Human Review")
        sha = calculate_file_sha256(final_path)
        self.state_mgr.initialize_lesson_state(lesson_id, source_sha256="src_sha_test")
        self.state_mgr.transition(lesson_id, "NEEDS_HUMAN_REVIEW", {"final_path": final_path, "final_sha256": sha})
        return final_path, sha

    def test_valid_human_acceptance_artifact_recorded(self):
        """Human approval creates a durable acceptance artifact and sets HUMAN_ACCEPTED."""
        final_path, final_sha = self._setup_final_file("M03-L08")

        chk = self.state_mgr.record_human_approval(
            lesson_id="M03-L08",
            reviewer="SME-Agile-Auditor",
            approved_final_sha256=final_sha,
            notes="Reviewed and approved 70% customer difficulty correction.",
        )
        self.assertEqual(chk["status"], "HUMAN_ACCEPTED")
        self.assertEqual(chk["verdict"], "HUMAN_ACCEPTED")
        self.assertIsNotNone(chk.get("acceptance_path"))
        self.assertTrue(os.path.exists(chk["acceptance_path"]))

        with open(chk["acceptance_path"], "r", encoding="utf-8") as af:
            art = json.load(af)
        self.assertEqual(art["decision"], "APPROVED")
        self.assertEqual(art["reviewer"], "SME-Agile-Auditor")
        self.assertEqual(art["approved_final_sha256"], final_sha)
        self.assertEqual(art["identity_verification"], "UNVERIFIED_CALLER_PROVIDED_IDENTITY")

    def test_subsequent_resume_preserves_valid_human_acceptance(self):
        """A valid HUMAN_ACCEPTED checkpoint resumes successfully without running inferences."""
        final_path, final_sha = self._setup_final_file("M03-L08")
        self.state_mgr.record_human_approval(
            lesson_id="M03-L08", reviewer="SME-Lead", approved_final_sha256=final_sha
        )
        self.assertTrue(self.state_mgr.is_resumable_pass("M03-L08", "src_sha_test"))

    def test_modified_final_invalidates_human_acceptance(self):
        """Modifying the final lesson after human approval invalidates the acceptance."""
        final_path, final_sha = self._setup_final_file("M03-L08")
        self.state_mgr.record_human_approval(
            lesson_id="M03-L08", reviewer="SME-Lead", approved_final_sha256=final_sha
        )
        self.assertTrue(self.state_mgr.is_resumable_pass("M03-L08", "src_sha_test"))

        # Modify final file
        with open(final_path, "w", encoding="utf-8") as f:
            f.write("# Modified final content post-human-approval")

        self.assertFalse(self.state_mgr.is_resumable_pass("M03-L08", "src_sha_test"))
        chk = self.state_mgr.load_checkpoint("M03-L08")
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_FINAL_OUTPUT_MODIFIED")

    def test_missing_or_modified_approval_artifact_invalidates_acceptance(self):
        """Tampering with or deleting the acceptance artifact invalidates HUMAN_ACCEPTED."""
        final_path, final_sha = self._setup_final_file("M03-L08")
        chk = self.state_mgr.record_human_approval(
            lesson_id="M03-L08", reviewer="SME-Lead", approved_final_sha256=final_sha
        )
        artifact_path = chk["acceptance_path"]

        # Tamper artifact
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write('{"decision": "TAMPERED"}')

        self.assertFalse(self.state_mgr.is_resumable_pass("M03-L08", "src_sha_test"))
        chk2 = self.state_mgr.load_checkpoint("M03-L08")
        self.assertEqual(chk2["status"], "INVALIDATED")

    def test_caller_supplied_reviewer_name_alone_cannot_falsify_approval(self):
        """Approval requires matching final SHA256; empty reviewer or wrong hash is rejected."""
        final_path, final_sha = self._setup_final_file("M03-L08")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_human_approval(
                lesson_id="M03-L08", reviewer="   ", approved_final_sha256=final_sha
            )
        self.assertIn("Reviewer identifier is required", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_human_approval(
                lesson_id="M03-L08", reviewer="SME-Lead", approved_final_sha256="wrong_hash"
            )
        self.assertIn("SHA256 mismatch", str(ctx.exception))

    def test_history_records_correct_from_and_to_status(self):
        """Event history captures from_status before transitioning to new status."""
        final_path, final_sha = self._setup_final_file("M03-L08")
        chk = self.state_mgr.record_human_approval(
            lesson_id="M03-L08", reviewer="SME-Lead", approved_final_sha256=final_sha
        )
        history = chk["history"]
        last_event = history[-1]
        self.assertEqual(last_event["from_status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(last_event["to_status"], "HUMAN_ACCEPTED")

    def test_human_acceptance_cannot_be_confused_with_ai_audit_pass(self):
        """HUMAN_ACCEPTED is distinct from AI audit PASS and does not fabricate AI evidence."""
        final_path, final_sha = self._setup_final_file("M03-L08")
        chk = self.state_mgr.record_human_approval(
            lesson_id="M03-L08", reviewer="SME-Lead", approved_final_sha256=final_sha
        )
        self.assertEqual(chk["status"], "HUMAN_ACCEPTED")
        self.assertNotEqual(chk["status"], "PASS")
        self.assertIsNone(chk.get("audit_path"))
        self.assertIsNone(chk.get("audit_sha256"))


class TestR2B04ModelVerification(BaseR2TestCase):
    """R2-B04: Fail-closed model verification policy across Worker, Auditor, and Repair."""

    def setUp(self):
        super().setUp()
        self.controller = CourseHarnessController(self.config_path, mode_override="automated_cli")
        self.controller.adapter.resolved_binary = "/bin/mock-agy"

    @patch("subprocess.run")
    def test_correct_reported_model_verified(self, mock_run):
        """Envelope reporting exact pinned model is marked VERIFIED."""
        envelope = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "conv-test",
            "response": "# Output",
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(envelope), stderr="")
        _, meta = self.controller.adapter._invoke_automated("prompt", "p.md", "worker", "M01-L07", "text", 1)

        self.assertEqual(meta["model_reported"], "gemini-3.8-flash-high")
        self.assertEqual(meta["model_verified"], "VERIFIED")

    @patch("subprocess.run")
    def test_different_model_rejected(self, mock_run):
        """Envelope reporting a fallback model is rejected with ModelUnavailableError."""
        envelope = {
            "status": "SUCCESS",
            "model": "gemini-1.5-flash",
            "conversation_id": "conv-test",
            "response": "# Output",
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(envelope), stderr="")

        with self.assertRaises(ModelUnavailableError) as ctx:
            self.controller.adapter._invoke_automated("prompt", "p.md", "worker", "M01-L07", "text", 1)
        self.assertIn("model mismatch", str(ctx.exception).lower())
        self.assertEqual(self.controller.adapter.last_model_verified, "MISMATCH")

    @patch("subprocess.run")
    def test_missing_reported_model_becomes_not_verified(self, mock_run):
        """Envelope omitting model field is marked NOT_VERIFIED, never assuming requested model."""
        envelope = {
            "status": "SUCCESS",
            "conversation_id": "conv-test",
            "response": "# Output",
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(envelope), stderr="")
        _, meta = self.controller.adapter._invoke_automated("prompt", "p.md", "worker", "M01-L07", "text", 1)

        self.assertIsNone(meta["model_reported"])
        self.assertEqual(meta["model_verified"], "NOT_VERIFIED")

    @patch("subprocess.run")
    def test_not_verified_cannot_yield_verified_ai_pass(self, mock_run):
        """When require_model_verification is true, NOT_VERIFIED blocks PASS into NEEDS_HUMAN_REVIEW."""
        self.controller.config["execution"]["require_model_verification"] = True
        lesson_meta = self._create_mock_lesson_meta("M01-L07")

        # Mock Worker: model present
        worker_env = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "conv-w",
            "response": "# Draft",
        }
        # Mock Auditor: model missing -> NOT_VERIFIED
        audit_payload = self._create_valid_audit_dict("M01-L07", hashlib.sha256(b"# Draft").hexdigest())
        auditor_env = {
            "status": "SUCCESS",
            # model omitted!
            "conversation_id": "conv-a",
            "response": json.dumps(audit_payload),
        }

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=json.dumps(worker_env), stderr=""),
            MagicMock(returncode=0, stdout=json.dumps(auditor_env), stderr=""),
        ]

        # Patch state_mgr.is_resumable_pass to False so inference runs
        self.controller.state_mgr.is_resumable_pass = MagicMock(return_value=False)
        chk = self.controller.process_lesson("M01-L07", reset=True)

        self.assertEqual(chk["status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(chk["error_category"], "MODEL_NOT_VERIFIED_FOR_PASS")

    @patch("subprocess.run")
    def test_worker_unverified_blocks_pass_even_if_auditor_verified(self, mock_run):
        """If Worker inference is NOT_VERIFIED but Auditor is VERIFIED, PASS is still blocked."""
        self.controller.config["execution"]["require_model_verification"] = True
        lesson_meta = self._create_mock_lesson_meta("M01-L07")

        # Worker envelope omits model -> NOT_VERIFIED
        worker_env = {
            "status": "SUCCESS",
            "conversation_id": "conv-w",
            "response": "# Draft",
        }
        # Auditor envelope has model -> VERIFIED
        audit_payload = self._create_valid_audit_dict("M01-L07", hashlib.sha256(b"# Draft").hexdigest())
        auditor_env = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "conv-a",
            "response": json.dumps(audit_payload),
        }

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=json.dumps(worker_env), stderr=""),
            MagicMock(returncode=0, stdout=json.dumps(auditor_env), stderr=""),
        ]

        self.controller.state_mgr.is_resumable_pass = MagicMock(return_value=False)
        chk = self.controller.process_lesson("M01-L07", reset=True)

        self.assertEqual(chk["status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(chk["error_category"], "MODEL_NOT_VERIFIED_FOR_PASS")

    def test_no_silent_fallback(self):
        """Adapter strictly rejects initializing or invoking unpinned models."""
        adapter = AgyAdapter(mode="mock", model="gemini-1.5-pro", evidence_dir=self.evidence_dir)
        with self.assertRaises(ModelUnavailableError) as ctx:
            adapter.verify_environment()
        self.assertIn("Model pinning violation", str(ctx.exception))


class TestR2SmallConsistencyFixes(BaseR2TestCase):
    """Section 7 Consistency Fixes: bulk pilot execution guard and fidelity hazard scoping."""

    def test_pilot_automated_cli_blocked(self):
        """--pilot in automated_cli mode must be blocked under provider-use policy."""
        test_args = ["run.py", "--pilot", "--config", self.config_path]
        with patch.object(sys, "argv", test_args), \
             patch("course_harness.cli_adapter.AgyAdapter.verify_environment", return_value={"status": "VERIFIED"}):
            exit_code = main()
            self.assertEqual(exit_code, 3)

    def test_fidelity_hazard_lesson_scoping(self):
        """Lesson-specific hazard patterns (70% tree mortality) do not flag unrelated lessons."""
        text_with_claim = "Dự án ghi nhận 70% cây bị chết trong tháng đầu."
        # For M01-L07 (Agile Manifesto), this should NOT trigger issues
        issues_m01 = validate_source_fidelity_numerical_claims(text_with_claim, lesson_id="M01-L07")
        self.assertEqual(len(issues_m01), 0)

        # For M03-L08 (Activity Virtual Verde), it MUST trigger an issue
        issues_m03 = validate_source_fidelity_numerical_claims(text_with_claim, lesson_id="M03-L08")
        self.assertEqual(len(issues_m03), 1)
        self.assertIn("70% cây bị chết", issues_m03[0])

        # Generic issues (fabricated timestamps or ungrounded quiz claims) trigger for all lessons
        generic_text = "Phần giải thích tại [02:30 ước lượng] nêu đáp án chính thức là A."
        issues_generic = validate_source_fidelity_numerical_claims(generic_text, lesson_id="M01-L07")
        self.assertEqual(len(issues_generic), 2)


if __name__ == "__main__":
    unittest.main()
