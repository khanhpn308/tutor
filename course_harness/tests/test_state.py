"""Tests for State Management, Resumability, Fail-Closed Integrity, and Checkpoint Invalidation."""

import os
import shutil
import tempfile
import unittest

from course_harness.state import StateManager, calculate_file_sha256


class TestState(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.state_mgr = StateManager(self.test_dir, prompt_config_hash="hash_v1")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_valid_pass_artifacts(self, lesson_id: str = "M01-L01"):
        import json
        final_file = os.path.join(self.test_dir, f"{lesson_id}_final.md")
        audit_file = os.path.join(self.test_dir, f"{lesson_id}_audit.json")
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("# Final Lesson Content")

        final_sha = calculate_file_sha256(final_file)
        audit_payload = {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "summary": "Valid test audit report",
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
            "limitations": ["Test environment limitation"],
            "audited_final_sha256": final_sha,
            "audit_invocation_id": "test-conv-001",
            "model_verification": "VERIFIED",
        }
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(audit_payload, f, indent=2)

        audit_sha = calculate_file_sha256(audit_file)

        # Save trusted Controller audit receipt
        receipt_data = {
            "invocation_id": "test-conv-001",
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
            "source_sha256": "sha_abc",
            "prompt_config_hash": "hash_v1",
            "audit_report_sha256": audit_sha,
            "created_at": "2026-10-23T10:00:00Z",
        }
        self.state_mgr.save_audit_receipt(receipt_data)

        return final_file, final_sha, audit_file, audit_sha

    def test_initialize_fresh_checkpoint(self):
        chk = self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        self.assertEqual(chk["status"], "PENDING")
        self.assertEqual(chk["source_sha256"], "sha_abc")
        self.assertEqual(chk["prompt_config_hash"], "hash_v1")

    def test_state_transitions(self):
        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        chk = self.state_mgr.transition("M01-L01", "DRAFTED", {"draft_version": 1})
        self.assertEqual(chk["status"], "DRAFTED")
        self.assertEqual(chk["draft_version"], 1)

        chk = self.state_mgr.transition("M01-L01", "AUDITED", {"verdict": "PASS"})
        self.assertEqual(chk["status"], "AUDITED")
        self.assertEqual(chk["verdict"], "PASS")

        # History should track steps
        self.assertEqual(len(chk["history"]), 2)

    def test_resumable_pass_with_full_evidence(self):
        """A PASS checkpoint with all valid hashes and files must resume successfully."""
        final_file, final_sha, audit_file, audit_sha = self._create_valid_pass_artifacts("M01-L01")

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M01-L01",
            "PASS",
            {
                "final_path": final_file,
                "final_sha256": final_sha,
                "audit_path": audit_file,
                "audit_sha256": audit_sha,
                "audit_invocation_id": "test-conv-001",
                "evidence_class": "REAL_AGY_VERIFIED",
            },
        )

        self.assertTrue(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))
        # Different source hash should NOT be resumable PASS
        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L01", "different_sha"))

    def test_fail_closed_missing_final_sha256(self):
        """Missing or null final_sha256 must invalidate PASS checkpoint."""
        final_file, _, audit_file, audit_sha = self._create_valid_pass_artifacts("M01-L01")

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M01-L01",
            "PASS",
            {
                "final_path": final_file,
                "final_sha256": None,  # Omitted hash
                "audit_path": audit_file,
                "audit_sha256": audit_sha,
            },
        )

        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))
        chk = self.state_mgr.load_checkpoint("M01-L01")
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_FINAL_SHA256_MISSING")

    def test_fail_closed_missing_audit_sha256(self):
        """Missing or null audit_sha256 must invalidate PASS checkpoint."""
        final_file, final_sha, audit_file, _ = self._create_valid_pass_artifacts("M01-L01")

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M01-L01",
            "PASS",
            {
                "final_path": final_file,
                "final_sha256": final_sha,
                "audit_path": audit_file,
                "audit_sha256": "",  # Empty hash
            },
        )

        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))
        chk = self.state_mgr.load_checkpoint("M01-L01")
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_AUDIT_SHA256_MISSING")

    def test_fail_closed_missing_final_file(self):
        """Missing final output file on disk must invalidate PASS checkpoint."""
        final_file, final_sha, audit_file, audit_sha = self._create_valid_pass_artifacts("M01-L01")
        os.remove(final_file)

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M01-L01",
            "PASS",
            {
                "final_path": final_file,
                "final_sha256": final_sha,
                "audit_path": audit_file,
                "audit_sha256": audit_sha,
                "audit_invocation_id": "test-conv-001",
                "evidence_class": "REAL_AGY_VERIFIED",
            },
        )

        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))
        chk = self.state_mgr.load_checkpoint("M01-L01")
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_FINAL_OUTPUT_MISSING")

    def test_fail_closed_missing_audit_file(self):
        """Missing audit report file on disk must invalidate PASS checkpoint."""
        final_file, final_sha, audit_file, audit_sha = self._create_valid_pass_artifacts("M01-L01")
        os.remove(audit_file)

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M01-L01",
            "PASS",
            {
                "final_path": final_file,
                "final_sha256": final_sha,
                "audit_path": audit_file,
                "audit_sha256": audit_sha,
                "audit_invocation_id": "test-conv-001",
                "evidence_class": "REAL_AGY_VERIFIED",
            },
        )

        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))
        chk = self.state_mgr.load_checkpoint("M01-L01")
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_AUDIT_REPORT_MISSING")

    def test_legacy_pass_checkpoint_rejected(self):
        """Legacy checkpoints that have status PASS but omit artifact hashes must be rejected and invalidated."""
        chk = {
            "lesson_id": "M01-L07",
            "status": "PASS",
            "source_sha256": "sha_src_123",
            "prompt_config_hash": "hash_v1",
            "final_path": "some/final.md",
            "audit_path": "some/audit.json",
            "final_sha256": None,
            "audit_sha256": None,
        }
        self.state_mgr.save_checkpoint("M01-L07", chk)

        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L07", "sha_src_123"))
        updated_chk = self.state_mgr.load_checkpoint("M01-L07")
        self.assertEqual(updated_chk["status"], "INVALIDATED")

    def test_source_invalidation(self):
        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_v1")
        self.state_mgr.transition("M01-L01", "PASS")

        # Source hash changes
        chk2 = self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_v2")
        self.assertEqual(chk2["status"], "PENDING")
        self.assertEqual(chk2["source_sha256"], "sha_v2")

    def test_config_hash_invalidation(self):
        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_v1")
        self.state_mgr.transition("M01-L01", "PASS")

        # New state manager with different config hash
        mgr2 = StateManager(self.test_dir, prompt_config_hash="hash_v2")
        chk2 = mgr2.initialize_lesson_state("M01-L01", source_sha256="sha_v1")
        self.assertEqual(chk2["status"], "PENDING")
        self.assertEqual(chk2["prompt_config_hash"], "hash_v2")

    def test_modified_final_output_invalidates_pass(self):
        """If the final markdown output file is modified externally, PASS must be invalidated."""
        final_file, final_sha, audit_file, audit_sha = self._create_valid_pass_artifacts("M01-L01")

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M01-L01",
            "PASS",
            {
                "final_path": final_file,
                "final_sha256": final_sha,
                "audit_path": audit_file,
                "audit_sha256": audit_sha,
                "audit_invocation_id": "test-conv-001",
                "evidence_class": "REAL_AGY_VERIFIED",
            },
        )
        self.assertTrue(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))

        # Tamper final file
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("Tampered or modified curriculum text")

        # Now is_resumable_pass must fail and invalidate checkpoint
        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))
        chk = self.state_mgr.load_checkpoint("M01-L01")
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_FINAL_OUTPUT_MODIFIED")

    def test_modified_audit_report_invalidates_pass(self):
        """If the audit JSON report is modified externally, PASS must be invalidated."""
        final_file, final_sha, audit_file, audit_sha = self._create_valid_pass_artifacts("M01-L01")

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M01-L01",
            "PASS",
            {
                "final_path": final_file,
                "final_sha256": final_sha,
                "audit_path": audit_file,
                "audit_sha256": audit_sha,
                "audit_invocation_id": "test-conv-001",
                "evidence_class": "REAL_AGY_VERIFIED",
            },
        )
        self.assertTrue(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))

        # Modify audit report
        with open(audit_file, "w", encoding="utf-8") as f:
            f.write('{"verdict": "TAMPERED"}')

        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L01", "sha_abc"))
        chk = self.state_mgr.load_checkpoint("M01-L01")
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_AUDIT_REPORT_MODIFIED")

    def test_record_human_approval_binding(self):
        """Human approval binds to exact final SHA256 and transitions status to PASS."""
        final_file, final_sha, audit_file, audit_sha = self._create_valid_pass_artifacts("M03-L08")

        self.state_mgr.initialize_lesson_state("M03-L08", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M03-L08",
            "NEEDS_HUMAN_REVIEW",
            {
                "final_path": final_file,
                "final_sha256": final_sha,
                "audit_path": audit_file,
                "audit_sha256": audit_sha,
                "audit_invocation_id": "test-conv-001",
                "evidence_class": "REAL_AGY_VERIFIED",
            },
        )

        # Successful approval with matching hash
        updated = self.state_mgr.record_human_approval(
            lesson_id="M03-L08",
            reviewer="SME-Agile-Lead",
            approved_final_sha256=final_sha,
            notes="Verified 70% customer difficulty correction.",
        )
        self.assertEqual(updated["status"], "HUMAN_ACCEPTED")
        self.assertEqual(updated["human_approval"]["reviewer"], "SME-Agile-Lead")
        self.assertEqual(updated["human_approval"]["approved_final_sha256"], final_sha)
        self.assertTrue(os.path.exists(updated["acceptance_path"]))
        self.assertEqual(updated["history"][-1]["from_status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(updated["history"][-1]["to_status"], "HUMAN_ACCEPTED")

        # Approval attempt with mismatched hash must be rejected
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_human_approval(
                lesson_id="M03-L08",
                reviewer="SME-Agile-Lead",
                approved_final_sha256="mismatched_sha256_hash",
            )
        self.assertIn("SHA256 mismatch", str(ctx.exception))

    def test_record_audit_verdict_binding(self):
        """Audit verdict binds to exact final SHA256."""
        final_file, final_sha, audit_file, audit_sha = self._create_valid_pass_artifacts("M03-L08")

        self.state_mgr.initialize_lesson_state("M03-L08", source_sha256="sha_abc")
        self.state_mgr.transition(
            "M03-L08",
            "NEEDS_REAUDIT",
            {"final_path": final_file, "final_sha256": final_sha},
        )

        # Valid binding
        updated = self.state_mgr.record_audit_verdict(
            lesson_id="M03-L08",
            verdict="PASS",
            audit_path=audit_file,
            expected_final_sha256=final_sha,
            notes="Re-audit passed.",
        )
        self.assertEqual(updated["status"], "PASS")
        self.assertEqual(updated["audit_sha256"], audit_sha)

        # Mismatch final sha rejected
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M03-L08",
                verdict="PASS",
                audit_path=audit_file,
                expected_final_sha256="wrong_final_sha",
            )
        self.assertIn("final SHA256 mismatch", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
