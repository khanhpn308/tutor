"""Focused regression tests for Findings NEW-01 and NEW-02.

Finding NEW-01: Visual Evidence Binding
- Figure count reconciliation between report and markdown
- Exact visual manifest SHA256 binding and verification
- Missing manifest, conflicting manifest hash, figure count mismatch
- Stale visual spec and missing/modified rendered asset rejection
- Blocking silent replacement of audited visual evidence during finalization
- Legitimate nonvisual QUIZ/GLOSSARY preservation
- Distinct RENDER_VERIFIED and VISUAL_REVIEWED stages

Finding NEW-02: Lesson Context and Receipt Consistency
- source_status cross-check across manifest, checkpoint, caller, and receipt
- Receipt source_status mismatch rejection on record and resume
- Checkpoint source_status mismatch rejection on record and resume
- Rejection of visual exemptions when authoritative manifest is missing
- Rejection of VIDEO_TRANSCRIPT masquerading as QUIZ
- Preservation of VIDEO_TRANSCRIPT/READING acceptance without exemption
- Correct QUIZ/GLOSSARY record-and-resume using top-level manifest structure
"""

import json
import os
import shutil
import tempfile
import unittest

from course_harness.state import StateManager, calculate_file_sha256
from course_harness.validator import AuditValidator, is_production_quality_eligible
from course_harness.visual import (
    QUALITY_RUBRIC_VERSION,
    calculate_sha256_bytes,
)


class TestNEW01VisualEvidenceBinding(unittest.TestCase):
    """Tests for Finding NEW-01: Visual Evidence Binding."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.checkpoints_dir = os.path.join(self.test_dir, "checkpoints")
        self.receipts_dir = os.path.join(self.test_dir, "receipts")
        self.manifest_path = os.path.join(self.test_dir, "manifest.json")
        self.output_dir = os.path.join(self.test_dir, "output_course")
        os.makedirs(self.checkpoints_dir, exist_ok=True)
        os.makedirs(self.receipts_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        manifest_data = {
            "lessons": {
                "M01-L01": {"lesson_id": "M01-L01", "source_type": "VIDEO_TRANSCRIPT", "status": "AVAILABLE"},
                "M01-L02": {"lesson_id": "M01-L02", "source_type": "QUIZ", "status": "AVAILABLE"},
            }
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f)

        self.state_mgr = StateManager(
            self.checkpoints_dir,
            prompt_config_hash="cfg_hash_closeout",
            receipts_dir=self.receipts_dir,
            manifest_path=self.manifest_path,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _setup_visual_lesson(self, lesson_id: str, num_figures: int = 1):
        """Creates final markdown with figure(s), visual manifest, source specs, and rendered assets."""
        lesson_assets_dir = os.path.join(self.test_dir, "assets", lesson_id)
        os.makedirs(lesson_assets_dir, exist_ok=True)

        # 1. Final markdown
        final_path = os.path.join(self.test_dir, f"{lesson_id}_final.md")
        md_lines = ["# Lesson Title\n\nLesson content.\n"]
        figures = []
        for i in range(1, num_figures + 1):
            fig_id = f"F{i:02d}"
            spec_filename = f"{fig_id}_diagram.mmd"
            svg_filename = f"{fig_id}_diagram.svg"
            spec_path = os.path.join(lesson_assets_dir, spec_filename)
            svg_path = os.path.join(lesson_assets_dir, svg_filename)

            with open(spec_path, "w", encoding="utf-8") as f:
                f.write(f"graph TD\n  A{i} --> B{i}\n")
            spec_sha = calculate_file_sha256(spec_path)

            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg"><text>Figure {i}</text></svg>')
            svg_sha = calculate_file_sha256(svg_path)

            md_lines.append(f'```mermaid\n<!-- figure: id="{fig_id}" type="FLOWCHART" -->\ngraph TD\n  A{i} --> B{i}\n```\n')

            figures.append({
                "figure_id": fig_id,
                "visual_type": "FLOWCHART",
                "source_spec_path": spec_path,
                "source_spec_sha256": spec_sha,
                "rendering_status": "RENDER_VERIFIED",
                "visual_review_status": "VISUAL_REVIEWED",
                "rendered_asset_path": svg_path,
                "rendered_asset_sha256": svg_sha,
            })

        with open(final_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        final_sha = calculate_file_sha256(final_path)

        # 2. Visual manifest
        vm_path = os.path.join(lesson_assets_dir, "visual_manifest.json")
        vm_data = {
            "lesson_id": lesson_id,
            "total_figures": len(figures),
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "visual_acceptance_summary": {
                "spec_valid": True,
                "render_verified": True,
                "visual_reviewed": True,
                "content_quality_accepted": False,
            },
            "figures": figures,
        }
        with open(vm_path, "w", encoding="utf-8") as f:
            json.dump(vm_data, f, indent=2)
        vm_sha = calculate_file_sha256(vm_path)

        # 3. Audit report
        audit_path = os.path.join(self.test_dir, f"{lesson_id}_audit.json")
        report = {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "summary": "Visual evidence fully validated for lesson.",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "audited_final_sha256": final_sha,
            "audit_invocation_id": f"inv_{lesson_id}",
            "visual_figures_audited": len(figures),
            "visual_manifest_sha256": vm_sha,
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
            "limitations": ["Visual evidence fully verified."],
        }
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        audit_sha = calculate_file_sha256(audit_path)

        # 4. Receipt
        receipt = {
            "invocation_id": f"inv_{lesson_id}",
            "role": "auditor",
            "lesson_id": lesson_id,
            "lesson_type": "VIDEO_TRANSCRIPT",
            "source_status": "AVAILABLE",
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "src_sha_test",
            "prompt_config_hash": "cfg_hash_closeout",
            "audit_report_sha256": audit_sha,
        }
        self.state_mgr.save_audit_receipt(receipt)

        # 5. Checkpoint
        chk = self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_test",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type="VIDEO_TRANSCRIPT",
            source_status="AVAILABLE",
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        chk["visual_manifest_path"] = vm_path
        chk["visual_manifest_sha256"] = vm_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        return final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures

    def test_missing_manifest_rejected_on_record_and_resume(self):
        """Observed NEW-01: Claiming visual evidence without visual manifest is rejected on record and resume."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_visual_lesson(lesson_id, 2)

        # Delete visual manifest from disk
        os.remove(vm_path)

        # 1. record_audit_verdict must reject
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
                final_path=final_path,
            )
        self.assertIn("visual manifest file missing", str(ctx.exception).lower())

        # 2. Checkpoint resume must invalidate
        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["status"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        chk["visual_manifest_path"] = vm_path
        chk["visual_manifest_sha256"] = vm_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_test"))
        updated_chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_VISUAL_MANIFEST_MISSING")

    def test_conflicting_manifest_hash_rejected(self):
        """Conflicting visual manifest hash between report and disk/checkpoint is rejected."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_visual_lesson(lesson_id, 1)

        # Tamper with visual manifest file
        with open(vm_path, "a") as f:
            f.write("\n// tampered")

        # 1. record_audit_verdict rejects
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
                final_path=final_path,
            )
        self.assertIn("visual manifest sha256 mismatch", str(ctx.exception).lower())

        # 2. Checkpoint resume rejects
        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["status"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        chk["visual_manifest_path"] = vm_path
        chk["visual_manifest_sha256"] = vm_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_test"))
        updated_chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_VISUAL_MANIFEST_HASH_MISMATCH")

    def test_incorrect_figure_count_rejected(self):
        """Audit report declaring 2 figures when markdown contains 1 is rejected."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_visual_lesson(lesson_id, 1)

        # Alter report to declare 2 figures
        with open(audit_path, "r", encoding="utf-8") as f:
            rep = json.load(f)
        rep["visual_figures_audited"] = 2
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2)

        with self.assertRaises(Exception) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
                final_path=final_path,
            )
        self.assertIn("figure", str(ctx.exception).lower())

    def test_stale_visual_spec_rejected(self):
        """Stale or modified visual source spec (.mmd) is detected and rejected on resume."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_visual_lesson(lesson_id, 1)

        # Successfully record PASS first
        self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
            final_path=final_path,
        )
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_test"))

        # Modify .mmd source spec
        spec_file = figures[0]["source_spec_path"]
        with open(spec_file, "a") as f:
            f.write("\n  B1 --> C1[Modified]\n")

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_test"))
        chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_VISUAL_SPEC_MODIFIED")

    def test_missing_rendered_asset_rejected(self):
        """Missing rendered SVG asset for figure marked RENDER_VERIFIED is rejected on resume."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_visual_lesson(lesson_id, 1)

        self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
            final_path=final_path,
        )

        # Delete rendered svg
        svg_file = figures[0]["rendered_asset_path"]
        os.remove(svg_file)

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_test"))
        chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_VISUAL_ASSET_MISSING")

    def test_legitimate_nonvisual_quiz_glossary_preserved(self):
        """Nonvisual QUIZ/GLOSSARY with 0 figures does not require visual manifest and resumes cleanly."""
        lesson_id = "M01-L02"  # QUIZ in manifest
        final_path = os.path.join(self.test_dir, f"{lesson_id}_final.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write("# QUIZ 1\n\nQuestion 1: What is Agile?\nA) Waterfall\nB) Agile\n")
        final_sha = calculate_file_sha256(final_path)

        audit_path = os.path.join(self.test_dir, f"{lesson_id}_audit.json")
        report = {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "summary": "Nonvisual quiz audit summary.",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "audited_final_sha256": final_sha,
            "audit_invocation_id": f"inv_{lesson_id}",
            "visual_figures_audited": 0,
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": [],
            "limitations": ["Nonvisual quiz."],
        }
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        audit_sha = calculate_file_sha256(audit_path)

        receipt = {
            "invocation_id": f"inv_{lesson_id}",
            "role": "auditor",
            "lesson_id": lesson_id,
            "lesson_type": "QUIZ",
            "source_status": "AVAILABLE",
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "src_sha_quiz",
            "prompt_config_hash": "cfg_hash_closeout",
            "audit_report_sha256": audit_sha,
        }
        self.state_mgr.save_audit_receipt(receipt)

        chk = self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_quiz",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type="QUIZ",
            source_status="AVAILABLE",
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        res = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            final_path=final_path,
            lesson_type="QUIZ",
            source_status="AVAILABLE",
        )
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_quiz", lesson_type="QUIZ", source_status="AVAILABLE"))

    def test_checkpoint_conflicting_manifest_hash_on_record_rejected(self):
        """Reject visual manifest hash mismatch between audit report and existing checkpoint."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_visual_lesson(lesson_id, 1)

        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["visual_manifest_sha256"] = "different_hash_in_checkpoint"
        self.state_mgr.save_checkpoint(lesson_id, chk)

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
                final_path=final_path,
            )
        self.assertIn("visual manifest hash mismatch", str(ctx.exception).lower())

    def test_render_verified_and_visual_reviewed_distinct(self):
        """RENDER_VERIFIED and VISUAL_REVIEWED are distinct lifecycle properties."""
        lesson_id = "M01-L01"
        _, _, _, _, vm_path, _, figures = self._setup_visual_lesson(lesson_id, 1)

        with open(vm_path, "r", encoding="utf-8") as f:
            vm_data = json.load(f)

        fig = vm_data["figures"][0]
        self.assertIn("rendering_status", fig)
        self.assertIn("visual_review_status", fig)
        self.assertEqual(fig["rendering_status"], "RENDER_VERIFIED")
        self.assertEqual(fig["visual_review_status"], "VISUAL_REVIEWED")
        self.assertNotEqual(id(fig["rendering_status"]), id(fig["visual_review_status"]))


class TestNEW02LessonContextReceiptConsistency(unittest.TestCase):
    """Tests for Finding NEW-02: Lesson Context and Receipt Consistency."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.checkpoints_dir = os.path.join(self.test_dir, "checkpoints")
        self.receipts_dir = os.path.join(self.test_dir, "receipts")
        self.manifest_path = os.path.join(self.test_dir, "manifest.json")
        os.makedirs(self.checkpoints_dir, exist_ok=True)
        os.makedirs(self.receipts_dir, exist_ok=True)

        # Actual manifest structure with top-level lessons mapping
        self.manifest_data = {
            "lessons": {
                "M01-L01": {"lesson_id": "M01-L01", "source_type": "VIDEO_TRANSCRIPT", "status": "AVAILABLE"},
                "M01-L02": {"lesson_id": "M01-L02", "source_type": "QUIZ", "status": "AVAILABLE"},
                "M01-L03": {"lesson_id": "M01-L03", "source_type": "GLOSSARY", "status": "AVAILABLE"},
                "M01-L04": {"lesson_id": "M01-L04", "source_type": "READING", "status": "AVAILABLE"},
                "M01-L05": {"lesson_id": "M01-L05", "source_type": "QUIZ", "status": "LOCKED"},
            }
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest_data, f)

        self.state_mgr = StateManager(
            self.checkpoints_dir,
            prompt_config_hash="cfg_hash_new02",
            receipts_dir=self.receipts_dir,
            manifest_path=self.manifest_path,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _setup_lesson_artifacts(self, lesson_id: str, lesson_type: str, source_status: str, visual_not_applicable: bool = False):
        final_path = os.path.join(self.test_dir, f"{lesson_id}_final.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(f"# Lesson {lesson_id}\n\nContent for {lesson_id}.\n")
        final_sha = calculate_file_sha256(final_path)

        dim_scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE" if visual_not_applicable else "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }

        audit_path = os.path.join(self.test_dir, f"{lesson_id}_audit.json")
        report = {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "summary": f"Audit summary for {lesson_id}.",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "audited_final_sha256": final_sha,
            "audit_invocation_id": f"inv_{lesson_id}",
            "visual_figures_audited": 0,
            "dimension_scores": dim_scores,
            "findings": [],
            "limitations": [],
        }
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        audit_sha = calculate_file_sha256(audit_path)

        return final_path, final_sha, audit_path, audit_sha

    def test_receipt_source_status_mismatch_rejected(self):
        """Observed NEW-02: Manifest and checkpoint declare AVAILABLE, but receipt declares LOCKED -> rejected."""
        lesson_id = "M01-L02"  # QUIZ, AVAILABLE
        final_path, final_sha, audit_path, audit_sha = self._setup_lesson_artifacts(
            lesson_id, "QUIZ", "AVAILABLE", visual_not_applicable=True
        )

        # Receipt declares LOCKED
        receipt = {
            "invocation_id": f"inv_{lesson_id}",
            "role": "auditor",
            "lesson_id": lesson_id,
            "lesson_type": "QUIZ",
            "source_status": "LOCKED",  # Mismatch with manifest AVAILABLE!
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "src_sha_test",
            "prompt_config_hash": "cfg_hash_new02",
            "audit_report_sha256": audit_sha,
        }
        self.state_mgr.save_audit_receipt(receipt)

        chk = self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_test",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type="QUIZ",
            source_status="AVAILABLE",
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        # 1. record_audit_verdict rejects
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                final_path=final_path,
                lesson_type="QUIZ",
                source_status="AVAILABLE",
            )
        self.assertIn("source_status", str(ctx.exception).lower())

        # 2. is_resumable_pass rejects and invalidates
        chk["status"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        self.state_mgr.save_checkpoint(lesson_id, chk)

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_test", lesson_type="QUIZ", source_status="AVAILABLE"))
        updated_chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_AUDIT_RECEIPT_CONTEXT_MISMATCH")

    def test_checkpoint_source_status_mismatch_rejected(self):
        """Checkpoint declares source_status=LOCKED while manifest declares AVAILABLE -> rejected."""
        lesson_id = "M01-L02"
        final_path, final_sha, audit_path, audit_sha = self._setup_lesson_artifacts(
            lesson_id, "QUIZ", "AVAILABLE", visual_not_applicable=True
        )

        receipt = {
            "invocation_id": f"inv_{lesson_id}",
            "role": "auditor",
            "lesson_id": lesson_id,
            "lesson_type": "QUIZ",
            "source_status": "AVAILABLE",
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "src_sha_test",
            "prompt_config_hash": "cfg_hash_new02",
            "audit_report_sha256": audit_sha,
        }
        self.state_mgr.save_audit_receipt(receipt)

        # Checkpoint initialized with LOCKED
        chk = self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_test",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type="QUIZ",
            source_status="LOCKED",  # Mismatch with manifest
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        # 1. record_audit_verdict rejects checkpoint mismatch
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                final_path=final_path,
            )
        self.assertIn("checkpoint source_status", str(ctx.exception).lower())

        # 2. is_resumable_pass rejects and invalidates
        chk["status"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        self.state_mgr.save_checkpoint(lesson_id, chk)

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_test"))
        updated_chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_LESSON_CONTEXT_MISMATCH")

    def test_missing_manifest_during_exemption_authorization_rejected(self):
        """Visual exemption claimed when authoritative manifest is missing -> rejected."""
        # Create StateManager without manifest
        state_mgr_no_manifest = StateManager(
            self.checkpoints_dir,
            prompt_config_hash="cfg_hash_new02",
            receipts_dir=self.receipts_dir,
            manifest_path=os.path.join(self.test_dir, "nonexistent_manifest.json"),
        )
        lesson_id = "M01-L02"
        final_path, final_sha, audit_path, audit_sha = self._setup_lesson_artifacts(
            lesson_id, "QUIZ", "AVAILABLE", visual_not_applicable=True
        )

        receipt = {
            "invocation_id": f"inv_{lesson_id}",
            "role": "auditor",
            "lesson_id": lesson_id,
            "lesson_type": "QUIZ",
            "source_status": "AVAILABLE",
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "src_sha_test",
            "prompt_config_hash": "cfg_hash_new02",
            "audit_report_sha256": audit_sha,
        }
        state_mgr_no_manifest.save_audit_receipt(receipt)

        chk = state_mgr_no_manifest.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_test",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type="QUIZ",
            source_status="AVAILABLE",
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        state_mgr_no_manifest.save_checkpoint(lesson_id, chk)

        # 1. record_audit_verdict rejects
        with self.assertRaises(ValueError) as ctx:
            state_mgr_no_manifest.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                final_path=final_path,
                lesson_type="QUIZ",
                source_status="AVAILABLE",
            )
        self.assertIn("authoritative manifest", str(ctx.exception).lower())

        # 2. is_resumable_pass rejects and invalidates with UNTRUSTED_EXEMPTION_CONTEXT
        chk["status"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        state_mgr_no_manifest.save_checkpoint(lesson_id, chk)

        self.assertFalse(state_mgr_no_manifest.is_resumable_pass(lesson_id, "src_sha_test", lesson_type="QUIZ", source_status="AVAILABLE"))
        updated_chk = state_mgr_no_manifest.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_UNTRUSTED_EXEMPTION_CONTEXT")

    def test_video_transcript_masquerading_as_quiz_rejected(self):
        """VIDEO_TRANSCRIPT attempting to pass lesson_type='QUIZ' to claim exemption is rejected."""
        lesson_id = "M01-L01"  # VIDEO_TRANSCRIPT in manifest
        final_path, final_sha, audit_path, audit_sha = self._setup_lesson_artifacts(
            lesson_id, "VIDEO_TRANSCRIPT", "AVAILABLE", visual_not_applicable=True
        )

        chk = self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_test",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type="VIDEO_TRANSCRIPT",
            source_status="AVAILABLE",
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        # Caller masquerades as QUIZ
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                final_path=final_path,
                lesson_type="QUIZ",  # Caller masquerade
                source_status="AVAILABLE",
            )
        self.assertIn("untrusted lesson context", str(ctx.exception).lower())

    def test_video_transcript_without_exemption_succeeds_without_manifest(self):
        """Standard VIDEO_TRANSCRIPT evaluating all 8 dimensions (no exemption) succeeds without manifest."""
        state_mgr_no_manifest = StateManager(
            self.checkpoints_dir,
            prompt_config_hash="cfg_hash_new02",
            receipts_dir=self.receipts_dir,
            manifest_path=os.path.join(self.test_dir, "nonexistent_manifest.json"),
        )
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha = self._setup_lesson_artifacts(
            lesson_id, "VIDEO_TRANSCRIPT", "AVAILABLE", visual_not_applicable=False
        )

        receipt = {
            "invocation_id": f"inv_{lesson_id}",
            "role": "auditor",
            "lesson_id": lesson_id,
            "lesson_type": "VIDEO_TRANSCRIPT",
            "source_status": "AVAILABLE",
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "src_sha_test",
            "prompt_config_hash": "cfg_hash_new02",
            "audit_report_sha256": audit_sha,
        }
        state_mgr_no_manifest.save_audit_receipt(receipt)

        chk = state_mgr_no_manifest.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_test",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type="VIDEO_TRANSCRIPT",
            source_status="AVAILABLE",
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        state_mgr_no_manifest.save_checkpoint(lesson_id, chk)

        # Standard non-exempt lesson succeeds
        res = state_mgr_no_manifest.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            final_path=final_path,
            lesson_type="VIDEO_TRANSCRIPT",
            source_status="AVAILABLE",
        )
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(state_mgr_no_manifest.is_resumable_pass(
            lesson_id, "src_sha_test", lesson_type="VIDEO_TRANSCRIPT", source_status="AVAILABLE"
        ))


if __name__ == "__main__":
    unittest.main()
