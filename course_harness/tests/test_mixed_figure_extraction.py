"""Regression tests for COURSE-HARNESS-V1-MIXED-FIGURE-EXTRACTION-HOTFIX.

Verifies:
1. One explicit figure + one untagged Mermaid: reject or register both consistently.
2. Two explicit figures: accept.
3. Two standalone Mermaid figures with deterministic IDs: accept.
4. Duplicate references to the same Mermaid block: no double counting.
5. Mismatched FIGURE_START/FIGURE_END: reject with VISUAL_MARKER_MALFORMED.
6. Invalid or incomplete figure marker: reject with VISUAL_MARKER_MALFORMED.
7. Existing Case A (F01 vs F99): reject with VISUAL_FIGURE_ID_MISMATCH.
8. Existing Case B (different Mermaid contents): reject with VISUAL_SOURCE_CONTENT_MISMATCH.
9. Valid QUIZ/GLOSSARY without visuals: accept.
10. Correct multi-figure lesson: record PASS and resume True.
11. Untracked Mermaid after PASS: invalidate checkpoint with INVALIDATED_VISUAL_UNTRACKED_FIGURE.
"""

import json
import os
import shutil
import tempfile
import unittest

from course_harness.state import StateManager, calculate_file_sha256
from course_harness.visual import (
    QUALITY_RUBRIC_VERSION,
    check_figure_markers,
    extract_figures_from_markdown,
    normalize_mermaid_code,
    validate_figure_semantic_binding,
)


class TestMixedFigureExtraction(unittest.TestCase):
    """Test suite for mixed figure extraction and untracked Mermaid block detection."""

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
            prompt_config_hash="cfg_hash_mixed_test",
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
        custom_markdown: str = None,
    ):
        """Creates an end-to-end lesson fixture with customized markdown and manifest figures."""
        lesson_assets_dir = os.path.join(self.test_dir, "assets", lesson_id)
        os.makedirs(lesson_assets_dir, exist_ok=True)

        # 1. Final markdown
        final_path = os.path.join(self.test_dir, f"{lesson_id}_final.md")
        if custom_markdown is not None:
            with open(final_path, "w", encoding="utf-8") as f:
                f.write(custom_markdown)
        else:
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
            "summary": "Visual evidence binding verified.",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "audited_final_sha256": final_sha,
            "audit_invocation_id": f"inv_{lesson_id}",
            "visual_figures_audited": len(manifest_figures),
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
        if manifest_figure_specs:
            report["visual_manifest_sha256"] = vm_sha

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
            "source_sha256": "src_sha_mixed_test",
            "prompt_config_hash": "cfg_hash_mixed_test",
            "audit_report_sha256": audit_sha,
        }
        self.state_mgr.save_audit_receipt(receipt)

        # 5. Checkpoint
        chk = self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="src_sha_mixed_test",
            model_id="gemini-3.8-flash-high",
            effort="high",
            execution_mode="automated_cli",
            lesson_type=lesson_type,
            source_status=source_status,
        )
        chk["final_path"] = final_path
        chk["final_sha256"] = final_sha
        chk["visual_manifest_path"] = vm_path if manifest_figure_specs else None
        chk["visual_manifest_sha256"] = vm_sha if manifest_figure_specs else None
        self.state_mgr.save_checkpoint(lesson_id, chk)

        return final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, manifest_figures

    def test_one_explicit_figure_plus_one_untagged_mermaid_reject_unregistered(self):
        """1. One explicit figure + one untagged Mermaid: rejects when unregistered."""
        lesson_id = "M01-L01"
        mixed_markdown = (
            "# Lesson Title\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Registered Flow\n"
            "```mermaid\n"
            "graph TD\n"
            "  A --> B\n"
            "```\n"
            "*Hình F01: Registered Flow*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ luồng chính xác.\n"
            "> **Mục tiêu giáo dục:** Làm rõ luồng bài học.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:15]\n"
            "<!-- FIGURE_END: F01 -->\n\n"
            "### Phần nội dung bổ sung\n\n"
            "```mermaid\n"
            "graph TD\n"
            "  Extra1 --> Extra2\n"
            "```\n"
        )
        # Manifest only has F01
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[],
            manifest_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"}],
            custom_markdown=mixed_markdown,
        )

        # Verify extraction enumerates both Mermaid blocks and flags the untagged one
        figs = extract_figures_from_markdown(mixed_markdown)
        self.assertEqual(len(figs), 2)
        self.assertEqual(figs[0]["figure_id"], "F01")
        self.assertFalse(figs[0]["is_untracked"])
        self.assertTrue(figs[1]["is_untracked"])
        self.assertTrue(str(figs[1]["figure_id"]).startswith("UNTRACKED"))

        # Semantic validator must reject with VISUAL_UNTRACKED_FIGURE
        with open(vm_path, "r", encoding="utf-8") as f:
            vm_data = json.load(f)
        is_valid, err_cat, err_msg = validate_figure_semantic_binding(
            markdown_content=mixed_markdown,
            manifest_data=vm_data,
        )
        self.assertFalse(is_valid)
        self.assertEqual(err_cat, "VISUAL_UNTRACKED_FIGURE")

        # record_audit_verdict must reject
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
            )
        self.assertIn("VISUAL_UNTRACKED_FIGURE", str(ctx.exception))

        # is_resumable_pass must reject and invalidate
        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["status"] = "PASS"
        chk["verdict"] = "PASS"
        chk["evidence_class"] = "REAL_AGY_VERIFIED"
        chk["audit_invocation_id"] = f"inv_{lesson_id}"
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha
        chk["prompt_config_hash"] = "cfg_hash_mixed_test"
        self.state_mgr.save_checkpoint(lesson_id, chk)

        resumable = self.state_mgr.is_resumable_pass(lesson_id, "src_sha_mixed_test")
        self.assertFalse(resumable)
        chk_after = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(chk_after["status"], "INVALIDATED")
        self.assertEqual(chk_after["error_category"], "INVALIDATED_VISUAL_UNTRACKED_FIGURE")

    def test_one_explicit_figure_plus_one_deterministic_mermaid_registered_consistently(self):
        """1b. One explicit figure + one tagged Mermaid: accepts when registered consistently."""
        lesson_id = "M01-L01"
        mixed_markdown = (
            "# Lesson Title\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: First Figure\n"
            "```mermaid\n"
            "graph TD\n"
            "  A --> B\n"
            "```\n"
            "*Hình F01: First Figure*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ khối thứ nhất.\n"
            "> **Mục tiêu giáo dục:** Làm rõ nguyên lý 1.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:15]\n"
            "<!-- FIGURE_END: F01 -->\n\n"
            "#### Hình F02: Second Figure\n"
            "```mermaid\n"
            "graph TD\n"
            "  C --> D\n"
            "```\n"
            "*Hình F02: Second Figure*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ khối thứ hai.\n"
            "> **Mục tiêu giáo dục:** Làm rõ nguyên lý 2.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [01:20]\n"
        )
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[],
            manifest_figure_specs=[
                {"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"},
                {"figure_id": "F02", "mermaid_code": "graph TD\n  C --> D"},
            ],
            custom_markdown=mixed_markdown,
        )

        figs = extract_figures_from_markdown(mixed_markdown)
        self.assertEqual(len(figs), 2)
        self.assertEqual([f["figure_id"] for f in figs], ["F01", "F02"])
        self.assertFalse(figs[0]["is_untracked"])
        self.assertFalse(figs[1]["is_untracked"])

        # record_audit_verdict and is_resumable_pass must succeed
        res = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
        )
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_mixed_test"))

    def test_two_explicit_figures_accepted(self):
        """2. Two explicit figures: accepts when properly declared and mapped."""
        lesson_id = "M01-L01"
        specs = [
            {"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"},
            {"figure_id": "F02", "mermaid_code": "graph LR\n  X --> Y"},
        ]
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=specs,
            manifest_figure_specs=specs,
        )
        res = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
        )
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_mixed_test"))

    def test_two_standalone_mermaid_figures_with_deterministic_ids_accepted(self):
        """3. Two standalone Mermaid figures with deterministic IDs: accepts."""
        lesson_id = "M01-L01"
        standalone_markdown = (
            "# Lesson Title\n\n"
            "#### Hình F01: Standalone One\n"
            "```mermaid\n"
            "graph TD\n"
            "  A --> B\n"
            "```\n"
            "*Hình F01: Standalone One*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ thứ nhất độc lập.\n"
            "> **Mục tiêu giáo dục:** Mục tiêu 1.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:10]\n\n"
            "#### Hình F02: Standalone Two\n"
            "```mermaid\n"
            "graph LR\n"
            "  C --> D\n"
            "```\n"
            "*Hình F02: Standalone Two*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ thứ hai độc lập.\n"
            "> **Mục tiêu giáo dục:** Mục tiêu 2.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:45]\n"
        )
        specs = [
            {"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"},
            {"figure_id": "F02", "mermaid_code": "graph LR\n  C --> D"},
        ]
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[],
            manifest_figure_specs=specs,
            custom_markdown=standalone_markdown,
        )
        figs = extract_figures_from_markdown(standalone_markdown)
        self.assertEqual([f["figure_id"] for f in figs], ["F01", "F02"])
        self.assertFalse(any(f["is_untracked"] for f in figs))

        res = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
        )
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_mixed_test"))

    def test_duplicate_references_to_same_mermaid_block_no_double_counting(self):
        """4. Duplicate references to the same Mermaid block: no double counting."""
        markdown = (
            "# Lesson Title\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Only One Figure\n"
            "```mermaid\n"
            "graph TD\n"
            "  A --> B\n"
            "```\n"
            "*Hình F01: Only One Figure*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ khối duy nhất trong bài.\n"
            "> **Mục tiêu giáo dục:** Mục tiêu duy nhất.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:10]\n"
            "<!-- FIGURE_END: F01 -->\n"
        )
        figs = extract_figures_from_markdown(markdown)
        # Even though F01 has explicit wrapper and Mermaid block with matching caption, it must be extracted exactly once
        self.assertEqual(len(figs), 1)
        self.assertEqual(figs[0]["figure_id"], "F01")

    def test_mismatched_figure_start_and_figure_end_rejected(self):
        """5. Mismatched FIGURE_START/FIGURE_END: rejects with VISUAL_MARKER_MALFORMED."""
        lesson_id = "M01-L01"
        broken_markdown = (
            "# Lesson Title\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Figure Title\n"
            "```mermaid\n"
            "graph TD\n"
            "  A --> B\n"
            "```\n"
            "*Hình F01: Figure Title*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ khối minh họa.\n"
            "> **Mục tiêu giáo dục:** Mục tiêu học tập.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:10]\n"
            "<!-- FIGURE_END: F02 -->\n"
        )
        errors = check_figure_markers(broken_markdown)
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any("Mismatched figure marker" in e for e in errors))

        # validate_figure_semantic_binding rejects with VISUAL_MARKER_MALFORMED
        is_valid, err_cat, err_msg = validate_figure_semantic_binding(
            markdown_content=broken_markdown,
            manifest_data={"figures": [{"figure_id": "F01"}]},
        )
        self.assertFalse(is_valid)
        self.assertEqual(err_cat, "VISUAL_MARKER_MALFORMED")

        # record_audit_verdict rejects with VISUAL_MARKER_MALFORMED
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[],
            manifest_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"}],
            custom_markdown=broken_markdown,
        )
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
            )
        self.assertIn("VISUAL_MARKER_MALFORMED", str(ctx.exception))

    def test_invalid_or_incomplete_figure_marker_rejected(self):
        """6. Invalid or incomplete figure marker: rejects with VISUAL_MARKER_MALFORMED."""
        lesson_id = "M01-L01"
        incomplete_markdown = (
            "# Lesson Title\n\n"
            "<!-- FIGURE_START -->\n"
            "#### Hình F01: Figure Title\n"
            "```mermaid\n"
            "graph TD\n"
            "  A --> B\n"
            "```\n"
            "<!-- FIGURE_END: F01 -->\n"
        )
        errors = check_figure_markers(incomplete_markdown)
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any("Malformed or incomplete" in e for e in errors))

        is_valid, err_cat, err_msg = validate_figure_semantic_binding(
            markdown_content=incomplete_markdown,
            manifest_data={"figures": [{"figure_id": "F01"}]},
        )
        self.assertFalse(is_valid)
        self.assertEqual(err_cat, "VISUAL_MARKER_MALFORMED")

        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[],
            manifest_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"}],
            custom_markdown=incomplete_markdown,
        )
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
            )
        self.assertIn("VISUAL_MARKER_MALFORMED", str(ctx.exception))

    def test_existing_case_a_f01_vs_f99_rejected(self):
        """7. Existing Case A (F01 vs F99): rejects with VISUAL_FIGURE_ID_MISMATCH."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"}],
            manifest_figure_specs=[{"figure_id": "F99", "mermaid_code": "graph TD\n  A --> B"}],
        )
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
            )
        self.assertIn("VISUAL_FIGURE_ID_MISMATCH", str(ctx.exception))

    def test_existing_case_b_different_mermaid_contents_rejected(self):
        """8. Existing Case B (different Mermaid contents): rejects with VISUAL_SOURCE_CONTENT_MISMATCH."""
        lesson_id = "M01-L01"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  A1 --> B1"}],
            manifest_figure_specs=[{"figure_id": "F01", "mermaid_code": "graph TD\n  Different --> Diagram"}],
        )
        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_path,
                expected_final_sha256=final_sha,
                audit_invocation_id=f"inv_{lesson_id}",
                visual_manifest_path=vm_path,
                visual_manifest_sha256=vm_sha,
            )
        self.assertIn("VISUAL_SOURCE_CONTENT_MISMATCH", str(ctx.exception))

    def test_valid_nonvisual_quiz_glossary_without_visuals_accepted(self):
        """9. Valid QUIZ/GLOSSARY without visuals: accepts."""
        lesson_id = "M01-L02"
        quiz_md = "# Quiz Lesson\n\n1. Question 1\n2. Question 2\n"
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=[],
            manifest_figure_specs=[],
            lesson_type="QUIZ",
            source_status="AVAILABLE",
            custom_markdown=quiz_md,
        )
        res = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            lesson_type="QUIZ",
            source_status="AVAILABLE",
        )
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_mixed_test", lesson_type="QUIZ", source_status="AVAILABLE"))

    def test_correct_multifigure_lesson_record_pass_and_resume_true(self):
        """10. Correct multi-figure lesson: records PASS and resumes True."""
        lesson_id = "M01-L01"
        specs = [
            {"figure_id": "F01", "mermaid_code": "flowchart LR\n  L1 --> R1"},
            {"figure_id": "F02", "mermaid_code": "graph TD\n  Plan --> Exec --> Inspect"},
        ]
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=specs,
            manifest_figure_specs=specs,
        )
        res = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
        )
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_mixed_test"))

    def test_untracked_mermaid_after_pass_invalidates_checkpoint(self):
        """11. Untracked Mermaid after PASS: invalidates checkpoint with INVALIDATED_VISUAL_UNTRACKED_FIGURE."""
        lesson_id = "M01-L01"
        specs = [{"figure_id": "F01", "mermaid_code": "graph TD\n  A --> B"}]
        final_path, final_sha, audit_path, audit_sha, vm_path, vm_sha, figures = self._setup_lesson_fixture(
            lesson_id=lesson_id,
            md_figure_specs=specs,
            manifest_figure_specs=specs,
        )
        # Record PASS
        res = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id=f"inv_{lesson_id}",
            visual_manifest_path=vm_path,
            visual_manifest_sha256=vm_sha,
        )
        self.assertEqual(res["status"], "PASS")
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "src_sha_mixed_test"))

        # Tamper: append an untracked Mermaid diagram to final.md
        with open(final_path, "a", encoding="utf-8") as f:
            f.write("\n\n```mermaid\ngraph TD\n  Tampered --> Injected\n```\n")

        # In order to test untracked figure detection specifically rather than file hash mismatch,
        # update checkpoint and audit report hash binding to the new file hash
        tampered_sha = calculate_file_sha256(final_path)
        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["final_sha256"] = tampered_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        with open(audit_path, "r", encoding="utf-8") as af:
            rpt_data = json.load(af)
        rpt_data["audited_final_sha256"] = tampered_sha
        with open(audit_path, "w", encoding="utf-8") as af:
            json.dump(rpt_data, af, indent=2)
        rpt_sha = calculate_file_sha256(audit_path)

        chk = self.state_mgr.load_checkpoint(lesson_id)
        chk["audit_sha256"] = rpt_sha
        self.state_mgr.save_checkpoint(lesson_id, chk)

        receipt = self.state_mgr.get_audit_receipt(f"inv_{lesson_id}")
        receipt["audited_final_sha256"] = tampered_sha
        receipt["audit_report_sha256"] = rpt_sha
        self.state_mgr.save_audit_receipt(receipt)

        # Resume must now fail because of untracked Mermaid block
        resumable = self.state_mgr.is_resumable_pass(lesson_id, "src_sha_mixed_test")
        self.assertFalse(resumable)
        chk_after = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(chk_after["status"], "INVALIDATED")
        self.assertEqual(chk_after["error_category"], "INVALIDATED_VISUAL_UNTRACKED_FIGURE")


if __name__ == "__main__":
    unittest.main()
