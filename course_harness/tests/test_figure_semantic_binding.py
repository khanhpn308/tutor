"""Focused regression tests for COURSE-HARNESS-V1-FIGURE-SEMANTIC-BINDING-HOTFIX.

Verifies:
1. Markdown F01 vs manifest F99 rejected (Case A) with VISUAL_FIGURE_ID_MISMATCH on record and resume.
2. Same figure ID but different Mermaid code rejected (Case B) with VISUAL_SOURCE_CONTENT_MISMATCH on record and resume.
3. Duplicate manifest figure IDs rejected with VISUAL_FIGURE_ID_MISMATCH on record and resume.
4. Duplicate Markdown figure IDs rejected with VISUAL_FIGURE_ID_MISMATCH on record and resume.
5. Reordered figures with correct ID/content mapping accepted on record and resume.
6. Pipeline trailing newline convention and Mermaid code normalization.
7. Altered .mmd file after PASS invalidated on resume with VISUAL_SPEC_MODIFIED.
8. Valid nonvisual QUIZ/GLOSSARY lessons record PASS and resume cleanly.
9. Legitimate multi-figure lessons record PASS and resume cleanly.
10. Existing context and receipt checks remain strictly enforced.
"""

import json
import os
import shutil
import tempfile
import unittest

from course_harness.state import StateManager, calculate_file_sha256
from course_harness.visual import (
    QUALITY_RUBRIC_VERSION,
    calculate_sha256_bytes,
    extract_figures_from_markdown,
    normalize_mermaid_code,
    validate_figure_semantic_binding,
)


class TestFigureSemanticBinding(unittest.TestCase):
    """Test suite for deterministic figure identity and Mermaid content semantic binding."""

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
                "M01-L03": {"lesson_id": "M01-L03", "source_type": "GLOSSARY", "status": "AVAILABLE"},
            }
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f)

        self.state_mgr = StateManager(
            self.checkpoints_dir,
            prompt_config_hash="cfg_hash_semantic_test",
            receipts_dir=self.receipts_dir,
            manifest_path=self.manifest_path,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _setup_lesson_fixture(
        self,
        lesson_id: str,
        md_figure_specs: list,
        manifest_figure_specs: list,
        lesson_type: str = "VIDEO_TRANSCRIPT",
        source_status: str = "AVAILABLE",
    ):
        """Creates an end-to-end lesson fixture with customized markdown and manifest figures."""
        lesson_assets_dir = os.path.join(self.test_dir, "assets", lesson_id)
        os.makedirs(lesson_assets_dir, exist_ok=True)

        # 1. Final markdown
        final_path = os.path.join(self.test_dir, f"{lesson_id}_final.md")
        md_lines = [f"# Lesson {lesson_id}\n\nOverview content.\n"]
        for spec in md_figure_specs:
            fig_id = spec["figure_id"]
            title = spec.get("title", f"Figure {fig_id}")
            mmd_code = spec.get("mermaid_code", "graph TD\n  A --> B")
            caption = spec.get("caption", f"Hình {fig_id}: {title}")
            alt = spec.get("alt_text", f"Detailed alt text for figure {fig_id}")
            md_lines.append(
                f"<!-- FIGURE_START: {fig_id} -->\n"
                f"#### {caption}\n"
                f"```mermaid\n{mmd_code}\n```\n"
                f"*{caption}*\n"
                f"> **Mô tả trực quan (Alt text):** {alt}\n"
                f"> **Mục tiêu giáo dục:** Làm rõ nguyên lý {fig_id}\n"
                f"> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:15]\n"
                f"<!-- FIGURE_END: {fig_id} -->\n"
            )
        with open(final_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        final_sha = calculate_file_sha256(final_path)

        # 2. Manifest and assets
        manifest_figures = []
        for spec in manifest_figure_specs:
            fig_id = spec["figure_id"]
            mmd_code = spec.get("mermaid_code", "graph TD\n  A --> B")
            spec_filename = f"{fig_id}_diagram.mmd"
            svg_filename = f"{fig_id}_diagram.svg"
            spec_path = os.path.join(lesson_assets_dir, spec_filename)
            svg_path = os.path.join(lesson_assets_dir, svg_filename)

            # Trailing newline convention as written by VisualAssetManager
            with open(spec_path, "wb") as f:
                f.write((mmd_code.strip() + "\n").encode("utf-8"))
            spec_sha = calculate_file_sha256(spec_path)

            with open(svg_path, "wb") as f:
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg"><text>{fig_id}</text></svg>'.encode("utf-8"))
            svg_sha = calculate_file_sha256(svg_path)

            manifest_figures.append({
                "figure_id": fig_id,
                "visual_type": spec.get("visual_type", "FLOWCHART"),
                "source_spec_path": spec_path,
                "source_spec_sha256": spec_sha,
                "rendering_status": "RENDER_VERIFIED",
                "visual_review_status": "VISUAL_REVIEWED",
                "rendered_asset_path": svg_path,
                "rendered_asset_sha256": svg_sha,
            })

        vm_path = os.path.join(lesson_assets_dir, "visual_manifest.json")
        vm_data = {
            "lesson_id": lesson_id,
            "total_figures": len(manifest_figures),
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "visual_acceptance_summary": {
                "spec_valid": True,
                "render_verified": True,
                "visual_reviewed": True,
                "content_quality_accepted": False,
            },
            "figures": manifest_figures,
        }
        with open(vm_path, "w", encoding="utf-8") as f:
            json.dump(vm_data, f, indent=2)
        vm_sha = calculate_file_sha256(vm_path)

        # 3. Audit report
        audit_path = os.path.join(self.test_dir, f"{lesson_id}_audit.json")
        report = {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "summary": "Full visual evidence binding verified.",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "audited_final_sha256": final_sha,
            "audit_invocation_id": f"inv_{lesson_id}",
            "visual_figures_audited": len(manifest_figures),
            "visual_manifest_sha256": vm_sha,
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
                "VISUAL_PEDAGOGY": "MET" if manifest_figure_specs else "NOT_APPLICABLE",
            },
            "findings": [],
            "limitations": ["Visual evidence verified."],
        }
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        audit_sha = calculate_file_sha256(audit_path)

        # 4. Receipt
        receipt = {
            "invocation_id": f"inv_{lesson_id}",
            "role": "auditor",
            "lesson_id": lesson_id,
            "lesson_type": lesson_type,
            "source_status": source_status,
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "src_sha_sem_test",
            "prompt_config_hash": "cfg_hash_semantic_test",
            "audit_report_sha256": audit_sha,
        }
        self.state_mgr.save_audit_receipt(receipt)

        # 5. Checkpoint
        chk = self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_sem_test",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type=lesson_type,
            source_status=source_status,
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        chk["visual_manifest_path"] = vm_path
        chk["visual_manifest_sha256"] = vm_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        return final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, manifest_figures

    def test_case_a_markdown_f01_vs_manifest_f99_rejected(self):
        """Case A Reproduction: Final Markdown has F01, manifest has F99. Must reject with VISUAL_FIGURE_ID_MISMATCH."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"}],
            manifest_figure_specs=[{"figure_id": "F99", "mermaid_code": "graph TD\n  A --> B"}],
        )

        # 1. record_audit_verdict MUST reject with VISUAL_FIGURE_ID_MISMATCH
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
        self.assertIn("VISUAL_FIGURE_ID_MISMATCH", str(ctx.exception))
        self.assertIn("Figure ID mismatch", str(ctx.exception))

        # 2. Checkpoint resume MUST fail and invalidate with VISUAL_FIGURE_ID_MISMATCH
        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["status"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        chk["visual_manifest_path"] = vm_path
        chk["visual_manifest_sha256"] = vm_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_sem_test"))
        updated_chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_VISUAL_FIGURE_ID_MISMATCH")

    def test_case_b_same_id_different_mermaid_code_rejected(self):
        """Case B Reproduction: Same ID F01, but Markdown and .mmd have different diagrams. Must reject."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A1 --> B1"}],
            manifest_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  Different --> Diagram"}],
        )

        # 1. record_audit_verdict MUST reject with VISUAL_SOURCE_CONTENT_MISMATCH
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
        self.assertIn("VISUAL_SOURCE_CONTENT_MISMATCH", str(ctx.exception))
        self.assertIn("Mermaid content mismatch", str(ctx.exception))

        # 2. Checkpoint resume MUST fail and invalidate with VISUAL_SOURCE_CONTENT_MISMATCH
        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["status"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        chk["visual_manifest_path"] = vm_path
        chk["visual_manifest_sha256"] = vm_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_sem_test"))
        updated_chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_VISUAL_SOURCE_CONTENT_MISMATCH")

    def test_duplicate_manifest_figure_ids_rejected(self):
        """Duplicate figure IDs in visual manifest are detected and rejected on record and resume."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[
                {"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"},
                {"figure_id": "F02", "mermaid_code": "graph TD\n  C --> D"},
            ],
            manifest_figure_specs=[
                {"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"},
                {"figure_id": "F01", "mermaid_code": "graph TD\n  C --> D"},
            ],
        )

        # 1. record_audit_verdict rejects with VISUAL_FIGURE_ID_MISMATCH
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
        self.assertIn("VISUAL_FIGURE_ID_MISMATCH", str(ctx.exception))
        self.assertIn("Duplicate figure_id detected in visual manifest figures", str(ctx.exception))

        # 2. Checkpoint resume rejects with VISUAL_FIGURE_ID_MISMATCH
        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["status"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        chk["visual_manifest_path"] = vm_path
        chk["visual_manifest_sha256"] = vm_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_sem_test"))
        updated_chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_VISUAL_FIGURE_ID_MISMATCH")

    def test_duplicate_markdown_figure_ids_rejected(self):
        """Duplicate figure IDs in Markdown are detected and rejected on record and resume."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[
                {"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"},
                {"figure_id": "F01", "mermaid_code": "graph TD\n  C --> D"},
            ],
            manifest_figure_specs=[
                {"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"},
                {"figure_id": "F02", "mermaid_code": "graph TD\n  C --> D"},
            ],
        )

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
        self.assertIn("VISUAL_FIGURE_ID_MISMATCH", str(ctx.exception))
        self.assertIn("Duplicate figure_id detected in Markdown", str(ctx.exception))

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

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_sem_test"))
        updated_chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(updated_chk["status"], "INVALIDATED")
        self.assertEqual(updated_chk["error_category"], "INVALIDATED_VISUAL_FIGURE_ID_MISMATCH")

    def test_reordered_figures_accepted(self):
        """Reordered figures with correct ID/content mapping record PASS and resume cleanly."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[
                {"figure_id": "F02", "mermaid_code": "graph TD\n  Step2 --> Finish"},
                {"figure_id": "F01", "mermaid_code": "graph TD\n  Start --> Step1"},
            ],
            manifest_figure_specs=[
                {"figure_id": "F01", "mermaid_code": "graph TD\n  Start --> Step1"},
                {"figure_id": "F02", "mermaid_code": "graph TD\n  Step2 --> Finish"},
            ],
        )

        # 1. record PASS succeeds
        chk = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
            final_path=final_path,
        )
        self.assertEqual(chk["status"], "PASS")

        # 2. is_resumable_pass succeeds
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_sem_test"))

    def test_mermaid_normalization_and_trailing_newline_convention(self):
        """Mermaid normalization handles pipeline trailing newlines and trailing line spaces without masking differences."""
        # 1. Trailing newline convention
        code_no_newline = "graph TD\n  A --> B"
        code_with_newline = "graph TD\n  A --> B\n\n"
        self.assertEqual(
            normalize_mermaid_code(code_no_newline),
            normalize_mermaid_code(code_with_newline),
        )

        # 2. Windows CRLF vs Unix LF
        crlf_code = "graph TD\r\n  A --> B\r\n"
        lf_code = "graph TD\n  A --> B\n"
        self.assertEqual(
            normalize_mermaid_code(crlf_code),
            normalize_mermaid_code(lf_code),
        )

        # 3. Trailing whitespace per line
        trailing_spaces = "graph TD   \n  A --> B    "
        clean = "graph TD\n  A --> B"
        self.assertEqual(
            normalize_mermaid_code(trailing_spaces),
            normalize_mermaid_code(clean),
        )

        # 4. Embedded HTML comments stripped
        with_comment = "<!-- figure: id=\"F01\" -->\ngraph TD\n  A --> B"
        self.assertEqual(
            normalize_mermaid_code(with_comment),
            normalize_mermaid_code(clean),
        )

        # 5. Meaningful differences are NOT masked
        diff1 = "graph TD\n  A --> B"
        diff2 = "graph TD\n  A --> C"
        self.assertNotEqual(
            normalize_mermaid_code(diff1),
            normalize_mermaid_code(diff2),
        )

    def test_altered_mmd_after_pass_invalidated(self):
        """Altering .mmd file on disk after PASS is detected on resume, invalidating checkpoint."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"}],
            manifest_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"}],
        )

        # Initial PASS
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
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_sem_test"))

        # Alter .mmd on disk
        spec_path = figures[0]["source_spec_path"]
        with open(spec_path, "wb") as f:
            f.write(b"graph TD\n  A --> Tampered\n")

        # Resume must invalidate
        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_sem_test"))
        chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_VISUAL_SPEC_MODIFIED")

    def test_valid_nonvisual_quiz_glossary_record_and_resume(self):
        """Legitimate nonvisual QUIZ and GLOSSARY record and resume cleanly without visual manifest."""
        for lid, ltype in [("M01-L02", "QUIZ"), ("M01-L03", "GLOSSARY")]:
            final_path = os.path.join(self.test_dir, f"{lid}_final.md")
            with open(final_path, "w", encoding="utf-8") as f:
                f.write(f"# {ltype} content\n\nNonvisual instructional material.\n")
            final_sha = calculate_file_sha256(final_path)

            audit_path = os.path.join(self.test_dir, f"{lid}_audit.json")
            report = {
                "lesson_id": lid,
                "verdict": "PASS",
                "summary": "Nonvisual pass.",
                "quality_rubric_version": QUALITY_RUBRIC_VERSION,
                "content_quality_accepted": True,
                "quality_score": 100.0,
                "audited_final_sha256": final_sha,
                "audit_invocation_id": f"inv_{lid}",
                "visual_figures_audited": 0,
                "dimension_scores": {
                    "SOURCE_FIDELITY": "MET",
                    "CONTENT_COMPLETENESS": "MET",
                    "PEDAGOGICAL_QUALITY": "MET",
                    "TERMINOLOGY_CONSISTENCY": "MET",
                    "SOURCE_TRACEABILITY": "MET",
                    "CLARITY_ORGANIZATION": "MET",
                    "FORMATTING": "MET",
                    "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
                },
                "findings": [],
                "limitations": [],
            }
            with open(audit_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            audit_sha = calculate_file_sha256(audit_path)

            receipt = {
                "invocation_id": f"inv_{lid}",
                "role": "auditor",
                "lesson_id": lid,
                "lesson_type": ltype,
                "source_status": "AVAILABLE",
                "execution_mode": "automated_cli",
                "provider": "agy",
                "evidence_class": "REAL_AGY_VERIFIED",
                "model_requested": "gemini-3.8-flash-high",
                "model_reported": "gemini-3.8-flash-high",
                "model_verified": "VERIFIED",
                "terminal_status": "SUCCESS",
                "audited_final_sha256": final_sha,
                "source_sha256": "src_sha_sem_test",
                "prompt_config_hash": "cfg_hash_semantic_test",
                "audit_report_sha256": audit_sha,
            }
            self.state_mgr.save_audit_receipt(receipt)

            chk = self.state_mgr.initialize_lesson_state(
                lesson_id=lid,
                source_sha256="src_sha_sem_test",
                model_id="gemini-3.8-flash-high",
                effort="high",
                execution_mode="automated_cli",
                lesson_type=ltype,
                source_status="AVAILABLE",
            )
            chk["final_path"] = final_path
            chk["final_sha256"] = final_sha
            self.state_mgr.save_checkpoint(lid, chk)

            res = self.state_mgr.record_audit_verdict(
                lesson_id=lid,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lid}",
                final_path=final_path,
            )
            self.assertEqual(res["status"], "PASS")
            self.assertTrue(self.state_mgr.is_resumable_pass(lid, "src_sha_sem_test"))

    def test_legitimate_two_figure_lesson_record_and_resume(self):
        """Legitimate two-figure lesson records PASS and resumes cleanly."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[
                {"figure_id": "F01", "mermaid_code": "graph TD\n  Start --> Step1"},
                {"figure_id": "F02", "mermaid_code": "graph TD\n  Step2 --> Finish"},
            ],
            manifest_figure_specs=[
                {"figure_id": "F01", "mermaid_code": "graph TD\n  Start --> Step1"},
                {"figure_id": "F02", "mermaid_code": "graph TD\n  Step2 --> Finish"},
            ],
        )

        chk = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
            final_path=final_path,
        )
        self.assertEqual(chk["status"], "PASS")
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_sem_test"))


if __name__ == "__main__":
    unittest.main()
