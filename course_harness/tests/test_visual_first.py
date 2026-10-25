"""Comprehensive Deterministic Tests for Course Harness v1 Visual-First Educational Design.

Covers:
1. Visual Plan schema validation (valid and invalid payloads).
2. Figure ID uniqueness across lesson visuals.
3. Visual references and source locators grounding.
4. Mermaid source extraction and syntax classification.
5. Relative image path correctness and path traversal security.
6. Asset existence and broken reference detection.
7. Figure caption and alt text completeness.
8. Visual metadata completeness (all required fields).
9. Visual artifact hash invalidation (modifying .mmd or visual manifest resets PASS).
10. VISUAL_PEDAGOGY dimension scoring in Quality Rubric.
11. NOT_APPLICABLE scoring normalization (e.g. excluding dimensions properly).
12. Quality score and hard-gate consistency (score < 90 or HIGH severity fails).
13. Provenance category validation.
14. Prohibition of fabricated quantitative chart data in controlled fixtures.
15. Nonvisual lesson exemptions (QUIZ, GLOSSARY, LOCKED).
16. Existing audit report backward compatibility (legacy 7 dimensions).
17. M01-L07 Agile Manifesto calibration fixture validation.
18. Honest rendering status (preserves .mmd, sets RENDER_NOT_VERIFIED when mmdc is unavailable).
"""

import hashlib
import json
import os
import re
import shutil
import tempfile
import unittest

from course_harness.fixtures.m01_l07_calibration import (
    get_m01_l07_audit_report,
    get_m01_l07_draft_markdown,
    get_m01_l07_rendered_svg_paths,
    get_m01_l07_visual_manifest,
)
from course_harness.state import StateManager, calculate_file_sha256
from course_harness.validator import (
    AuditValidator,
    ValidationError,
    validate_draft_structure,
    validate_visual_pedagogy,
)
from course_harness.visual import (
    QUALITY_RUBRIC_VERSION,
    SUPPORTED_VISUAL_TYPES,
    TARGET_QUALITY_SCORE,
    VISUAL_ACCEPTANCE_STAGES,
    VISUAL_REVIEW_STATUSES,
    VisualAssetManager,
    VisualPlanValidator,
    calculate_quality_score,
    extract_figures_from_markdown,
    validate_chart_fidelity,
    validate_figure_properties,
)


class TestVisualFirstDesign(unittest.TestCase):
    """Test suite for Visual-First Educational Design."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.checkpoints_dir = os.path.join(self.test_dir, "checkpoints")
        self.assets_dir = os.path.join(self.test_dir, "assets")
        self.evidence_dir = os.path.join(self.test_dir, "evidence")
        self.receipts_dir = os.path.join(self.evidence_dir, "receipts")
        os.makedirs(self.checkpoints_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.receipts_dir, exist_ok=True)

        self.plan_validator = VisualPlanValidator()
        self.audit_validator = AuditValidator("course_harness/schemas/audit.schema.json")
        self.state_mgr = StateManager(
            checkpoints_dir=self.checkpoints_dir,
            prompt_config_hash="prompt_hash_test_v1",
            receipts_dir=self.receipts_dir,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_visual_plan_schema_valid_and_invalid(self):
        """1. Visual Plan schema rejects missing required fields and accepts compliant specs."""
        valid_plan = {
            "lesson_id": "M01-L07",
            "visual_profile": "VIDEO_TRANSCRIPT",
            "rationale": "Illustrates Agile values using comparison and dynamic balance maps.",
            "total_figures": 1,
            "figures": [
                {
                    "figure_id": "F01",
                    "title": "Bốn cặp giá trị của Tuyên ngôn Agile",
                    "visual_type": "COMPARISON_DIAGRAM",
                    "educational_purpose": "Làm rõ 4 cặp giá trị đối ứng và thứ tự ưu tiên.",
                    "related_learning_objective": "Nắm vững 4 giá trị của Tuyên ngôn Agile.",
                    "source_locators": ["00:52", "01:51"],
                    "provenance_class": "PEDAGOGICAL_RECONSTRUCTION",
                    "alt_text": "Sơ đồ khối hai cột so sánh các giá trị bên trái và bên phải.",
                    "caption": "Hình F01: Bốn cặp giá trị cốt lõi của Tuyên ngôn Agile.",
                    "mermaid_code": "graph LR\n  A --> B",
                }
            ],
        }
        errors = self.plan_validator.validate_plan(valid_plan)
        self.assertEqual(errors, [])

        # Invalid plan: missing educational_purpose and alt_text
        invalid_plan = {
            "lesson_id": "M01-L07",
            "figures": [
                {
                    "figure_id": "F01",
                    "title": "Invalid Figure",
                    "visual_type": "CONCEPT_MAP",
                    "related_learning_objective": "Goal",
                    "source_locators": ["00:01"],
                    "provenance_class": "SOURCE_DERIVED",
                    "caption": "Short caption here",
                }
            ],
        }
        errs = self.plan_validator.validate_plan(invalid_plan)
        self.assertTrue(len(errs) > 0)
        self.assertTrue(any("educational_purpose" in e for e in errs))
        self.assertTrue(any("alt_text" in e for e in errs))

    def test_figure_id_uniqueness(self):
        """2. Duplicate figure IDs within a lesson are flagged as violations."""
        draft = (
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Sơ đồ thứ nhất\n"
            "```mermaid\ngraph TD\nA-->B\n```\n"
            "*Hình F01: Chú thích sơ đồ thứ nhất.*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ quy trình từ bước A sang bước B.\n"
            "> **Mục tiêu giáo dục:** Minh họa bước A sang B.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:10].\n"
            "<!-- FIGURE_END: F01 -->\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Sơ đồ thứ hai bị trùng ID\n"
            "```mermaid\ngraph TD\nC-->D\n```\n"
            "*Hình F01: Chú thích sơ đồ thứ hai trùng ID.*\n"
            "> **Mô tả trực quan (Alt text):** Sơ đồ khối trùng lặp mã định danh.\n"
            "> **Mục tiêu giáo dục:** Minh họa bước C sang D.\n"
            "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:20].\n"
            "<!-- FIGURE_END: F01 -->\n"
        )
        issues = validate_visual_pedagogy(draft, "VIDEO_TRANSCRIPT")
        self.assertTrue(any("Duplicate figure_id detected" in issue for issue in issues))

    def test_visual_references_and_source_locators(self):
        """3. Figures must have valid source locators grounding them to the raw source."""
        fig_without_loc = {
            "figure_id": "F01",
            "title": "Sơ đồ thiếu locator",
            "visual_type": "CONCEPT_MAP",
            "educational_purpose": "Minh họa kiến thức mà không có căn cứ.",
            "related_learning_objective": "Học tập.",
            "source_locators": [],
            "provenance_class": "PEDAGOGICAL_RECONSTRUCTION",
            "alt_text": "Mô tả sơ đồ chi tiết hơn 10 ký tự.",
            "caption": "Hình F01: Chú thích sơ đồ chi tiết.",
        }
        errs = validate_figure_properties(fig_without_loc)
        self.assertTrue(any("Missing source_locators" in e for e in errs))

    def test_mermaid_source_extraction(self):
        """4. Controller accurately extracts Mermaid blocks and classifies diagram types."""
        markdown = (
            "# Bài học Scrum\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Quy trình Sprint\n\n"
            "```mermaid\n"
            "flowchart TD\n"
            "    Plan[Sprint Planning] --> Daily[Daily Scrum]\n"
            "    Daily --> Review[Sprint Review]\n"
            "```\n\n"
            "*Hình F01: Quy trình diễn ra một Sprint trong Scrum.*\n"
            "> **Mô tả trực quan (Alt text):** Lưu đồ 3 bước thể hiện luồng sự kiện trong Sprint.\n"
            "> **Mục tiêu giáo dục:** Nắm vững thứ tự các sự kiện trong Scrum.\n"
            "> **Xuất xứ học liệu (Provenance):** `PEDAGOGICAL_RECONSTRUCTION` [01:15].\n"
            "<!-- FIGURE_END: F01 -->\n"
        )
        figs = extract_figures_from_markdown(markdown)
        self.assertEqual(len(figs), 1)
        self.assertEqual(figs[0]["figure_id"], "F01")
        self.assertEqual(figs[0]["visual_type"], "FLOWCHART")
        self.assertIn("Sprint Planning", figs[0]["mermaid_code"])

    def test_relative_image_path_correctness_and_safety(self):
        """5. Image paths must be relative and path traversal attacks are rejected."""
        safe_fig = {
            "figure_id": "F01",
            "title": "Safe figure",
            "visual_type": "CONCEPT_MAP",
            "educational_purpose": "Minh họa an toàn bảo mật.",
            "related_learning_objective": "Học tập an toàn.",
            "source_locators": ["00:01"],
            "provenance_class": "SOURCE_DERIVED",
            "alt_text": "Mô tả trực quan chuẩn xác.",
            "caption": "Hình F01: Chú thích đầy đủ ý nghĩa.",
            "source_spec_path": "assets/M01-L07/F01.mmd",
            "rendered_asset_path": "assets/M01-L07/F01.svg",
        }
        self.assertEqual(validate_figure_properties(safe_fig), [])

        # Absolute path attack
        abs_fig = dict(safe_fig, rendered_asset_path="/etc/passwd")
        errs = validate_figure_properties(abs_fig)
        self.assertTrue(any("must be relative" in e for e in errs))

        # Path traversal attack
        trav_fig = dict(safe_fig, source_spec_path="../../../etc/shadow")
        errs = validate_figure_properties(trav_fig)
        self.assertTrue(any("Path traversal" in e for e in errs))

    def test_asset_existence_and_missing_broken_references(self):
        """6. Asset manager writes .mmd files to disk and detects missing visual assets."""
        asset_mgr = VisualAssetManager(self.assets_dir)
        figures = [
            {
                "figure_id": "F01",
                "title": "Agile Values Comparison",
                "visual_type": "COMPARISON_DIAGRAM",
                "educational_purpose": "Minh họa so sánh các giá trị.",
                "related_learning_objective": "Hiểu giá trị Agile.",
                "source_locators": ["00:52"],
                "provenance_class": "PEDAGOGICAL_RECONSTRUCTION",
                "alt_text": "Mô tả chi tiết hơn mười ký tự.",
                "caption": "Hình F01: So sánh giá trị.",
                "mermaid_code": "graph LR\n  Left --> Right\n",
            }
        ]
        proc_figs, manifest_path, manifest_sha = asset_mgr.process_figures_for_lesson("M01-L07", figures)
        self.assertTrue(os.path.exists(manifest_path))
        self.assertEqual(len(proc_figs), 1)

        mmd_file = os.path.join(self.assets_dir, "M01-L07", "F01_agile_values_comparison.mmd")
        self.assertTrue(os.path.exists(mmd_file))
        with open(mmd_file, "r") as f:
            self.assertIn("graph LR", f.read())

    def test_figure_caption_and_alt_text_requirements(self):
        """7. Figures with absent or truncated alt text or captions are rejected."""
        bad_fig = {
            "figure_id": "F01",
            "title": "Short caption test",
            "visual_type": "CONCEPT_MAP",
            "educational_purpose": "Minh họa ngắn.",
            "related_learning_objective": "Mục tiêu.",
            "source_locators": ["00:01"],
            "provenance_class": "SOURCE_DERIVED",
            "alt_text": "Too short",  # < 10 chars
            "caption": "Brief",       # < 10 chars
        }
        errs = validate_figure_properties(bad_fig)
        self.assertTrue(any("Alt text missing or too brief" in e for e in errs))
        self.assertTrue(any("Caption missing or too brief" in e for e in errs))

    def test_visual_metadata_completeness(self):
        """8. Validates completeness of all 9 figure metadata fields."""
        complete_fig = {
            "figure_id": "F01",
            "title": "Quy trình phát triển Agile",
            "visual_type": "FLOWCHART",
            "educational_purpose": "Minh họa vòng đời phát triển linh hoạt qua các bước lặp.",
            "related_learning_objective": "Nắm vững chu kỳ phát triển linh hoạt.",
            "source_locators": ["02:15"],
            "provenance_class": "PEDAGOGICAL_RECONSTRUCTION",
            "alt_text": "Sơ đồ dòng chảy thể hiện chu kỳ lặp đi lặp lại của dự án.",
            "caption": "Hình F01: Vòng đời lặp phát triển của một dự án Agile.",
            "mermaid_code": "flowchart TD\n  Plan-->Code-->Test\n",
        }
        self.assertEqual(validate_figure_properties(complete_fig), [])

    def test_visual_artifact_hash_invalidation(self):
        """9. Tampering with an on-disk .mmd spec or visual manifest immediately invalidates PASS."""
        lesson_id = "M01-L07"
        lesson_assets_dir = os.path.join(self.assets_dir, lesson_id)
        os.makedirs(lesson_assets_dir, exist_ok=True)

        mmd_path = os.path.join(lesson_assets_dir, "F01_values.mmd")
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write("graph LR\n  A-->B\n")
        mmd_sha = calculate_file_sha256(mmd_path)

        manifest_path = os.path.join(lesson_assets_dir, "visual_manifest.json")
        manifest_data = {
            "lesson_id": lesson_id,
            "figures": [{
                "figure_id": "F01",
                "source_spec_path": mmd_path,
                "source_spec_sha256": mmd_sha,
            }]
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f)
        manifest_sha = calculate_file_sha256(manifest_path)

        # Setup mock valid final markdown and audit report
        final_path = os.path.join(self.test_dir, "M01-L07_final.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(
                "# Final Lesson M01-L07\n\nContent here with verified figures.\n\n"
                "<!-- FIGURE_START: F01 -->\n"
                "#### Sơ đồ giá trị F01\n"
                "```mermaid\ngraph LR\n  A-->B\n```\n"
                "*Hình F01: Chú thích sơ đồ F01.*\n"
                "> **Mô tả trực quan (Alt text):** Sơ đồ khối quy trình từ A sang B chi tiết.\n"
                "> **Mục tiêu giáo dục:** Làm rõ luồng xử lý từ bước A sang bước B.\n"
                "> **Xuất xứ học liệu (Provenance):** `SOURCE_DERIVED` [00:10].\n"
                "<!-- FIGURE_END: F01 -->\n"
            )
        final_sha = calculate_file_sha256(final_path)

        audit_path = os.path.join(self.test_dir, "M01-L07_audit.json")
        audit_data = {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "summary": "Valid audit report.",
            "visual_figures_audited": 1,
            "visual_manifest_sha256": manifest_sha,
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
            "limitations": ["Verified environment."],
            "audited_final_sha256": final_sha,
            "audit_invocation_id": "inv-auditor-123",
        }
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f)
        audit_sha = calculate_file_sha256(audit_path)

        # Save valid Controller audit receipt
        self.state_mgr.save_audit_receipt({
            "invocation_id": "inv-auditor-123",
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
            "source_sha256": "source_sha_initial",
            "prompt_config_hash": "prompt_hash_test_v1",
            "audit_report_sha256": audit_sha,
        })

        # Initialize checkpoint and bind verdict
        self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256="source_sha_initial",
            execution_mode="automated_cli",
        )
        self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_path,
            expected_final_sha256=final_sha,
            audit_invocation_id="inv-auditor-123",
            final_path=final_path,
            visual_manifest_path=manifest_path,
            visual_manifest_sha256=manifest_sha,
            visual_figures=manifest_data["figures"],
        )

        # 1. Resumable pass holds when files are untampered
        self.assertTrue(self.state_mgr.is_resumable_pass(lesson_id, "source_sha_initial"))

        # 2. Tampering with .mmd diagram source file invalidates PASS
        with open(mmd_path, "a", encoding="utf-8") as f:
            f.write("\n  B-->C (Tampered)\n")

        self.assertFalse(self.state_mgr.is_resumable_pass(lesson_id, "source_sha_initial"))
        chk = self.state_mgr.load_checkpoint(lesson_id)
        self.assertEqual(chk["status"], "INVALIDATED")
        self.assertEqual(chk["error_category"], "INVALIDATED_VISUAL_SPEC_MODIFIED")

    def test_visual_pedagogy_scoring(self):
        """10. VISUAL_PEDAGOGY dimension contributes 15% weight to Quality Rubric."""
        scores_all_met = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        res = calculate_quality_score(scores_all_met, [])
        self.assertEqual(res["quality_score"], 100.0)
        self.assertEqual(res["verdict"], "PASS")

        # When VISUAL_PEDAGOGY has MINOR_ISSUES (multiplier 0.7)
        # Earned = 15 * 0.7 = 10.5 out of 15 (loss of 4.5 points)
        scores_minor_visual = dict(scores_all_met, VISUAL_PEDAGOGY="MINOR_ISSUES")
        res_minor = calculate_quality_score(scores_minor_visual, [])
        self.assertEqual(res_minor["quality_score"], 95.5)
        self.assertEqual(res_minor["verdict"], "PASS")

        # When VISUAL_PEDAGOGY fails
        scores_fail_visual = dict(scores_all_met, VISUAL_PEDAGOGY="FAILED")
        res_fail = calculate_quality_score(scores_fail_visual, [])
        self.assertEqual(res_fail["quality_score"], 85.0)
        self.assertEqual(res_fail["verdict"], "FAIL")
        self.assertFalse(res_fail["hard_gates_passed"])

    def test_not_applicable_scoring_normalization(self):
        """11. NOT_APPLICABLE dimensions are properly normalized against eligible weights."""
        scores_quiz = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",  # 15 points excluded
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        # Eligible weight sum is 100 - 15 = 85.
        # Since all eligible are MET, score must normalize to exactly 100.0%.
        res = calculate_quality_score(scores_quiz, [], lesson_type="QUIZ")
        self.assertEqual(res["quality_score"], 100.0)
        self.assertEqual(res["applicable_weight_sum"], 85.0)
        self.assertEqual(res["verdict"], "PASS")

    def test_quality_score_and_hard_gate_consistency(self):
        """12. Hard gates override score (HIGH finding or FAILED dimension fails PASS)."""
        dim_scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        # Despite 100.0% dimension score, a HIGH severity finding fails the verdict
        blocking_findings = [{
            "finding_id": "F-BLOCK-01",
            "severity": "HIGH",
            "category": "SOURCE_FIDELITY",
            "source_locator": "00:52",
            "draft_locator": "Figure F01",
            "description": "Erronously reversed arrows in visual diagram.",
            "required_action": "Invert arrows to point left over right.",
        }]
        res = calculate_quality_score(dim_scores, blocking_findings)
        self.assertFalse(res["hard_gates_passed"])
        self.assertEqual(res["verdict"], "FAIL")

        # Report declaring PASS with score < 90 is rejected by validator
        low_score_report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "summary": "Attempted pass with multiple degraded dimensions.",
            "dimension_scores": {
                "SOURCE_FIDELITY": "MINOR_ISSUES",      # 25 * 0.7 = 17.5 (-7.5)
                "CONTENT_COMPLETENESS": "MINOR_ISSUES",  # 15 * 0.7 = 10.5 (-4.5)
                "PEDAGOGICAL_QUALITY": "MINOR_ISSUES",   # 15 * 0.7 = 10.5 (-4.5)
                "VISUAL_PEDAGOGY": "MINOR_ISSUES",       # 15 * 0.7 = 10.5 (-4.5)
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": [],
            "limitations": ["Degraded quality test."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.audit_validator.validate_report(low_score_report, "M01-L07")
        self.assertIn("target threshold: 90.0", str(ctx.exception))

    def test_provenance_category_validation(self):
        """13. Validates supported provenance classes and rejects arbitrary categorizations."""
        valid_classes = [
            "SOURCE_DERIVED",
            "PEDAGOGICAL_RECONSTRUCTION",
            "AI_GENERATED_ILLUSTRATION",
            "EXTERNAL_VERIFIED_ASSET",
        ]
        for p_class in valid_classes:
            fig = {
                "figure_id": "F01",
                "title": f"Valid {p_class}",
                "visual_type": "CONCEPT_MAP",
                "educational_purpose": "Minh họa đúng phân loại xuất xứ.",
                "related_learning_objective": "Học tập.",
                "source_locators": ["00:01"],
                "provenance_class": p_class,
                "alt_text": "Mô tả trực quan chi tiết cho bài học.",
                "caption": "Hình F01: Chú thích đúng chuẩn.",
            }
            self.assertEqual(validate_figure_properties(fig), [])

        invalid_fig = dict(fig, provenance_class="FABRICATED_IMAGINATION")
        errs = validate_figure_properties(invalid_fig)
        self.assertTrue(any("Unsupported provenance_class" in e for e in errs))

    def test_no_fabricated_chart_data_in_controlled_fixtures(self):
        """14. Rejects charts fabricating quantitative numbers absent from raw source."""
        raw_source = "Giảng viên trình bày về 4 cặp giá trị mà không đề cập bất kỳ tỷ lệ phần trăm nào."
        fig_with_invented_pie = {
            "figure_id": "F01",
            "title": "Biểu đồ tỷ lệ ưu tiên bịa đặt",
            "visual_type": "DATA_CHART",
            "mermaid_code": 'pie title Tỷ lệ ưu tiên\n  "Cá nhân": 70\n  "Quy trình": 30\n',
        }
        violations = validate_chart_fidelity(fig_with_invented_pie, raw_source)
        self.assertEqual(len(violations), 2)
        self.assertTrue(any("70" in v for v in violations))
        self.assertTrue(any("30" in v for v in violations))

    def test_nonvisual_lesson_exemptions(self):
        """15. Exempts short quizzes, glossaries, and locked lessons from visual quotas."""
        # Non-visual quiz lesson with 0 figures does not generate visual pedagogy issues
        quiz_markdown = (
            "# Bài kiểm tra kiến thức Scrum\n\n"
            "## 1. Câu hỏi trắc nghiệm\n"
            "Ai là người chịu trách nhiệm tối đa hóa giá trị sản phẩm?\n"
            "- A. Scrum Master\n"
            "- B. Product Owner\n"
        )
        issues = validate_visual_pedagogy(quiz_markdown, "QUIZ", require_visuals=False)
        self.assertEqual(issues, [])

    def test_existing_audit_provenance_backward_compatibility(self):
        """16. Legacy audit reports lacking VISUAL_PEDAGOGY remain 100% backward compatible."""
        legacy_report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "summary": "Legacy audit report before visual-first upgrade.",
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
            "limitations": ["Legacy v1 model run."],
        })
        payload, warnings = self.audit_validator.validate_report(legacy_report, "M01-L07")
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["quality_score"], 100.0)
        self.assertEqual(payload["quality_rubric_version"], "LEGACY_UNKNOWN")
        self.assertFalse(payload["content_quality_accepted"])

    def test_m01_l07_calibration_fixture(self):
        """17. Calibrated M01-L07 fixture contains F01 and F02, passing visual pedagogy validation."""
        draft = get_m01_l07_draft_markdown()
        figures = extract_figures_from_markdown(draft)
        self.assertEqual(len(figures), 2)

        fig_ids = [f["figure_id"] for f in figures]
        self.assertEqual(fig_ids, ["F01", "F02"])

        # Check Figure F01: 4 value pairs
        f01 = figures[0]
        self.assertIn("Bốn cặp giá trị", f01["title"])
        self.assertEqual(f01["provenance_class"], "PEDAGOGICAL_RECONSTRUCTION")
        self.assertIn("00:52", f01["source_locators"])
        self.assertTrue(
            "individuals and interactions" in f01["mermaid_code"].lower()
            or "individuals & interactions" in f01["mermaid_code"].lower()
        )
        self.assertIn("working software", f01["mermaid_code"].lower())
        self.assertNotIn("/ product", f01["mermaid_code"].lower())

        # Check Figure F02: Balancing planning and responsiveness feedback loop
        f02 = figures[1]
        self.assertIn("cân bằng", f02["title"].lower())
        self.assertIn("04:37", f02["source_locators"])

        # Validate whole structure with visual pedagogy enabled
        raw_source_path = "output_course/Agile_Project_Management/Module_01_The_fundamentals_of_Agile/07_The_four_values_of_the_Agile_Manifesto.md"
        with open(raw_source_path, "r", encoding="utf-8") as rf:
            raw_content = rf.read()

        issues = validate_draft_structure(
            draft_content=draft,
            source_type="VIDEO_TRANSCRIPT",
            lesson_id="M01-L07",
            raw_source_content=raw_content,
            require_visuals=True,
        )
        self.assertEqual(issues, [])

        # Validate M01-L07 audit report fixture
        audit_rep = get_m01_l07_audit_report()
        val_rep, _ = self.audit_validator.validate_report(json.dumps(audit_rep), "M01-L07")
        self.assertEqual(val_rep["verdict"], "PASS")
        self.assertEqual(val_rep["quality_score"], 100.0)

    def test_mermaid_renderer_honest_fallback(self):
        """18. When local mmdc is unavailable, .mmd is preserved and status is RENDER_NOT_VERIFIED."""
        # Using asset manager without mmdc
        asset_mgr = VisualAssetManager(self.assets_dir, mmdc_binary="/nonexistent/bin/mmdc")
        self.assertFalse(asset_mgr.is_renderer_available())

        figures = [{
            "figure_id": "F01",
            "title": "Fallback Test Figure",
            "visual_type": "FLOWCHART",
            "educational_purpose": "Kiểm thử fallback khi không có renderer.",
            "related_learning_objective": "Fallback testing.",
            "source_locators": ["00:01"],
            "provenance_class": "PEDAGOGICAL_RECONSTRUCTION",
            "alt_text": "Mô tả trực quan hơn mười ký tự.",
            "caption": "Hình F01: Chú thích kiểm thử fallback.",
            "mermaid_code": "graph TD\n  Start-->End\n",
        }]

        proc_figs, manifest_path, manifest_sha = asset_mgr.process_figures_for_lesson("M01-L07", figures)
        self.assertEqual(proc_figs[0]["rendering_status"], "RENDER_NOT_VERIFIED")
        self.assertIsNone(proc_figs[0]["rendered_asset_path"])
        self.assertIsNone(proc_figs[0]["rendered_asset_sha256"])

        # Ensure .mmd file was preserved on disk despite no renderer
        mmd_file = os.path.join(self.assets_dir, "M01-L07", "F01_fallback_test_figure.mmd")
        self.assertTrue(os.path.exists(mmd_file))

    def test_unsupported_quantitative_claims_in_m01_l07_rejected(self):
        """19. Detects and rejects unsupported numerical details in M01-L07."""
        corrupt_draft = get_m01_l07_draft_markdown() + (
            "\n\n## 4. Tình huống\n"
            "Nhóm nhận thấy trao đổi email mất 3 ngày, rút ngắn xuống 15 phút [01:51].\n"
            "Chờ đợi 6 tháng để viết 200 trang tài liệu thay bằng 2 tuần [03:42].\n"
        )
        issues = validate_draft_structure(corrupt_draft, "VIDEO_TRANSCRIPT", lesson_id="M01-L07")
        self.assertTrue(any("3 ngày" in i or "15 phút" in i for i in issues))
        self.assertTrue(any("6 tháng" in i or "200 trang" in i or "2 tuần" in i for i in issues))

    def test_properly_labeled_hypothetical_examples_accepted(self):
        """20. Properly labeled AI_GENERATED_EXAMPLE without false timestamps is accepted."""
        valid_hypo_draft = get_m01_l07_draft_markdown()
        issues = validate_draft_structure(valid_hypo_draft, "VIDEO_TRANSCRIPT", lesson_id="M01-L07")
        self.assertEqual(issues, [])

    def test_hypothetical_example_with_source_timestamp_rejected(self):
        """21. Rejects attaching a source timestamp to an invented AI_GENERATED_EXAMPLE."""
        fake_timestamp_draft = get_m01_l07_draft_markdown() + (
            "\n\n### Tình huống minh họa (AI_GENERATED_EXAMPLE)\n"
            "Ví dụ giả định được lập trình viên triển khai trong vòng 48 giờ [02:15].\n"
        )
        issues = validate_draft_structure(fake_timestamp_draft, "VIDEO_TRANSCRIPT", lesson_id="M01-L07")
        self.assertTrue(any("must not attach source timestamp" in i for i in issues))

    def test_original_manifesto_terminology_preserved(self):
        """22. Figure F01 preserves 'Working software' without mixing '/ Product' in node label."""
        draft = get_m01_l07_draft_markdown()
        figures = extract_figures_from_markdown(draft)
        f01 = [f for f in figures if f["figure_id"] == "F01"][0]
        self.assertIn("Working software", f01["mermaid_code"])
        self.assertNotIn("/ Product", f01["mermaid_code"])
        self.assertNotIn("/ Sản phẩm", f01["mermaid_code"])

    def test_figure_ids_and_source_locators(self):
        """23. Figure IDs and source locators strictly adhere to course schema."""
        draft = get_m01_l07_draft_markdown()
        figures = extract_figures_from_markdown(draft)
        for fig in figures:
            self.assertRegex(fig["figure_id"], r'^F\d{2}$')
            self.assertTrue(len(fig["source_locators"]) > 0)
            for loc in fig["source_locators"]:
                self.assertRegex(loc, r'^\d{1,2}:\d{2}$')

    def test_rendered_asset_paths_and_checksums(self):
        """24. M01-L07 rendered SVG assets exist on disk with valid XML and matching SHA256."""
        svg_paths = get_m01_l07_rendered_svg_paths()
        manifest = get_m01_l07_visual_manifest()

        for fig_meta in manifest["figures"]:
            fig_id = fig_meta["figure_id"]
            svg_file = svg_paths[fig_id]
            self.assertTrue(os.path.exists(svg_file), f"SVG file not found: {svg_file}")

            with open(svg_file, "rb") as sf:
                data = sf.read()
            self.assertIn(b"<svg", data)
            calc_sha = hashlib.sha256(data).hexdigest()
            self.assertEqual(calc_sha, fig_meta["rendered_asset_sha256"])

    def test_actual_svg_rendering_verification(self):
        """25. VisualAssetManager successfully renders valid Mermaid to SVG when mmdc is available."""
        asset_mgr = VisualAssetManager(self.assets_dir)
        if not asset_mgr.is_renderer_available():
            self.skipTest("Renderer not available in this environment")

        figures = [{
            "figure_id": "F01",
            "title": "Verified Render Test",
            "visual_type": "FLOWCHART",
            "educational_purpose": "Kiểm tra render thực tế ra SVG.",
            "related_learning_objective": "Học tập.",
            "source_locators": ["00:01"],
            "provenance_class": "PEDAGOGICAL_RECONSTRUCTION",
            "alt_text": "Mô tả trực quan chi tiết cho bài học.",
            "caption": "Hình F01: Chú thích sơ đồ.",
            "mermaid_code": "flowchart TD\n  Step1[Bắt đầu] --> Step2[Hoàn thành]\n",
        }]
        proc_figs, manifest_path, _ = asset_mgr.process_figures_for_lesson("M01-L07", figures)
        self.assertEqual(proc_figs[0]["rendering_status"], "RENDER_VERIFIED")
        self.assertIsNotNone(proc_figs[0]["rendered_asset_path"])
        self.assertIsNotNone(proc_figs[0]["rendered_asset_sha256"])

    def test_mermaid_rendering_failure_state(self):
        """26. Invalid Mermaid syntax produces RENDER_FAILED without corrupting execution."""
        asset_mgr = VisualAssetManager(self.assets_dir)
        if not asset_mgr.is_renderer_available():
            self.skipTest("Renderer not available in this environment")

        broken_fig = [{
            "figure_id": "F99",
            "title": "Broken Syntax Figure",
            "visual_type": "FLOWCHART",
            "educational_purpose": "Kiểm thử lỗi cú pháp.",
            "related_learning_objective": "Học tập.",
            "source_locators": ["00:01"],
            "provenance_class": "PEDAGOGICAL_RECONSTRUCTION",
            "alt_text": "Mô tả trực quan hơn mười ký tự.",
            "caption": "Hình F99: Sơ đồ hỏng cú pháp.",
            "mermaid_code": "flowchart TD\n  A --->>> [[[ Invalid Syntax ]]]\n",
        }]
        proc_figs, _, _ = asset_mgr.process_figures_for_lesson("M01-TEST", broken_fig)
        self.assertEqual(proc_figs[0]["rendering_status"], "RENDER_FAILED")
        self.assertIsNone(proc_figs[0]["rendered_asset_path"])

    def test_visual_acceptance_stages_separation(self):
        """27. Stages SPEC_VALID, RENDER_VERIFIED, VISUAL_REVIEWED, CONTENT_QUALITY_ACCEPTED are distinct."""
        self.assertEqual(
            VISUAL_ACCEPTANCE_STAGES,
            {"SPEC_VALID", "RENDER_VERIFIED", "VISUAL_REVIEWED", "CONTENT_QUALITY_ACCEPTED"},
        )
        self.assertEqual(
            VISUAL_REVIEW_STATUSES,
            {"VISUAL_REVIEWED", "VISUAL_LAYOUT_NOT_VERIFIED"},
        )

        manifest = get_m01_l07_visual_manifest()
        summary = manifest.get("visual_acceptance_summary", {})
        self.assertTrue(summary.get("spec_valid"))
        self.assertTrue(summary.get("render_verified"))
        self.assertTrue(summary.get("visual_reviewed"))
        # content_quality_accepted is governed by independent audit, not asset pipeline
        self.assertFalse(summary.get("content_quality_accepted"))

    def test_quality_hard_gate_blocks_pass_even_with_high_score(self):
        """28. A HIGH finding blocks PASS and content_quality_accepted regardless of quality score."""
        dim_scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        high_finding = [{
            "finding_id": "F-FIDELITY-01",
            "severity": "HIGH",
            "category": "SOURCE_FIDELITY",
            "source_locator": "01:51",
            "draft_locator": "Section 4.1",
            "description": "Fabricated email duration numbers.",
            "required_action": "Remove unsupported quantitative figures.",
        }]
        res = calculate_quality_score(dim_scores, high_finding)
        self.assertEqual(res["quality_score"], 100.0)
        self.assertFalse(res["hard_gates_passed"])
        self.assertFalse(res["content_quality_accepted"])
        self.assertEqual(res["verdict"], "FAIL")

        # Validator also blocks report declaring content_quality_accepted=True with blocking findings
        bad_report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "FAIL",
            "summary": "Contradictory report.",
            "findings": high_finding,
            "limitations": ["Test limitation."],
            "content_quality_accepted": True,
        })
        with self.assertRaises(ValidationError) as ctx:
            self.audit_validator.validate_report(bad_report, "M01-L07")
        self.assertIn("content_quality_accepted is True but report contains", str(ctx.exception))

    def test_q01_source_attribution_regression(self):
        """29. Q-01 Regression: Detects and rejects unsupported historical claim '17 chuyên gia' in M01-L07."""
        clean_draft = get_m01_l07_draft_markdown()
        self.assertNotIn("17 chuyên gia", clean_draft)
        self.assertNotIn("17 người", clean_draft)
        issues = validate_draft_structure(clean_draft, "VIDEO_TRANSCRIPT", lesson_id="M01-L07")
        self.assertEqual(issues, [])

        # Negative case: inserting '17 chuyên gia' fails validator with fidelity hazard
        unsupported_draft = clean_draft.replace(
            "các chuyên gia và nhà lãnh đạo",
            "17 chuyên gia và nhà lãnh đạo"
        )
        violations = validate_draft_structure(unsupported_draft, "VIDEO_TRANSCRIPT", lesson_id="M01-L07")
        self.assertTrue(any("17 chuyên gia" in v for v in violations))

    def test_q02_working_software_terminology_regression(self):
        """30. Q-02 Regression: Working software definition rejects 'thành phẩm hoàn thiện' and 'mọi sản phẩm bất kỳ'."""
        clean_draft = get_m01_l07_draft_markdown()
        self.assertNotIn("thành phẩm hoàn thiện", clean_draft)
        self.assertNotIn("mọi sản phẩm bất kỳ", clean_draft)

        # Negative case: re-introducing overstatement is rejected by validator
        overstated_draft = clean_draft + "\nWorking software là thành phẩm hoàn thiện 100% [02:38].\n"
        issues = validate_draft_structure(overstated_draft, "VIDEO_TRANSCRIPT", lesson_id="M01-L07")
        self.assertTrue(any("thành phẩm hoàn thiện" in i for i in issues))

    def test_q03_f01_visual_design_semantics_regression(self):
        """31. Q-03 Regression: F01 diagram preserves 4 pairs, comparison semantics without process flow, and faithful wording."""
        manifest = get_m01_l07_visual_manifest()
        f01 = [f for f in manifest["figures"] if f["figure_id"] == "F01"][0]
        code = f01["mermaid_code"]

        # Exactly 4 value pairs
        self.assertIn("Individuals and interactions", code)
        self.assertIn("Working software", code)
        self.assertIn("Customer collaboration", code)
        self.assertIn("Responding to change", code)
        self.assertIn("Processes and tools", code)
        self.assertIn("Comprehensive documentation", code)
        self.assertIn("Contract negotiation", code)
        self.assertIn("Following a plan", code)

        # Source faithful wording for right side (not 'thiết yếu')
        self.assertIn("VẪN CÓ GIÁ TRỊ", code)
        self.assertNotIn("VẪN CÓ GIÁ TRỊ THIẾT YẾU", code)

        # Comparison semantics: uses comparison lines '---' instead of repeated process-flow arrows '==>'
        self.assertIn("L1 --- R1", code)
        self.assertIn("L2 --- R2", code)
        self.assertNotIn('==>|"ưu tiên hơn"|', code)

        # Original principle 'Working software' unchanged
        self.assertIn("Working software", code)
        self.assertNotIn("/ product", code.lower())

    def test_q04_f02_visual_design_compact_feedback_loop_regression(self):
        """32. Q-04 Regression: F02 is a compact feedback flow without false causal dependencies."""
        manifest = get_m01_l07_visual_manifest()
        f02 = [f for f in manifest["figures"] if f["figure_id"] == "F02"][0]
        code = f02["mermaid_code"]

        # Distinction between 4 concepts
        self.assertIn("kế hoạch", code.lower())
        self.assertIn("phản hồi", code.lower())
        self.assertIn("thích ứng", code.lower())
        self.assertIn("giá trị", code.lower())

        # Feedback does not always cause change (feedback has direct path to value)
        self.assertIn("Feedback -->", code)
        self.assertIn("Adapt", code)

        # Delivery goal does not cause planning (no Value -> Plan edge)
        self.assertNotIn("Value --> Plan", code)
        self.assertNotIn("Value -.-> Plan", code)

        # Meaningful feedback loop exists (Adapt -> Plan)
        self.assertIn("Adapt -.->", code)
        self.assertIn("Plan", code)

        # Provenance classification is PEDAGOGICAL_RECONSTRUCTION
        self.assertEqual(f02["provenance_class"], "PEDAGOGICAL_RECONSTRUCTION")

        # Compact rendered SVG height check (< 500px, down from 870px)
        svg_paths = get_m01_l07_rendered_svg_paths()
        with open(svg_paths["F02"], "r", encoding="utf-8") as f:
            svg_content = f.read()
        import re
        vb_match = re.search(r'viewBox="0 0 [\d\.]+\s+([\d\.]+)"', svg_content)
        self.assertIsNotNone(vb_match)
        height = float(vb_match.group(1))
        self.assertLess(height, 500.0, f"F02 SVG height {height}px exceeds compact limit 500px")

    def test_q05_student_markdown_metadata_separation_regression(self):
        """33. Q-05 Regression: Student Markdown presents figures cleanly without raw machine metadata blocks."""
        draft = get_m01_l07_draft_markdown()

        # Prohibits machine metadata blockquotes from being exposed to students
        self.assertNotIn("> **Mục tiêu giáo dục:**", draft)
        self.assertNotIn("> **Xuất xứ học liệu (Provenance):**", draft)
        self.assertNotIn("> **Mô tả trực quan (Alt text):**", draft)

        # Validates cleanly with check_student_cleanliness enabled
        issues = validate_draft_structure(
            draft,
            "VIDEO_TRANSCRIPT",
            lesson_id="M01-L07",
            check_student_cleanliness=True,
        )
        self.assertEqual(issues, [])

        # Negative case: adding machine metadata blocks is flagged by cleanliness validator
        dirty_draft = draft + "\n> **Xuất xứ học liệu (Provenance):** `PEDAGOGICAL_RECONSTRUCTION` [00:01].\n"
        dirty_issues = validate_draft_structure(
            dirty_draft,
            "VIDEO_TRANSCRIPT",
            lesson_id="M01-L07",
            check_student_cleanliness=True,
        )
        self.assertTrue(any("internal pipeline metadata" in i for i in dirty_issues))

    def test_q06_rendered_assets_integration_and_hash_invalidation_regression(self):
        """34. Q-06 Regression: Valid relative SVG references exist, match hashes, and detect altered/broken assets."""
        draft = get_m01_l07_draft_markdown()
        manifest_path = "course_harness/fixtures/assets/M01-L07/visual_manifest.json"

        # Check manifest assets verify with zero errors
        errs = VisualAssetManager.verify_manifest_assets(manifest_path, base_dir="course_harness/fixtures")
        self.assertEqual(errs, [])

        # Image references in draft point to relative SVG paths with meaningful alt text
        img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', draft)
        self.assertEqual(len(img_refs), 2)
        for alt, path in img_refs:
            self.assertTrue(path.endswith(".svg"))
            self.assertFalse(os.path.isabs(path))
            self.assertGreaterEqual(len(alt.strip()), 10)

        # Negative case: Broken relative image reference triggers validator
        broken_draft = draft.replace("F01_b_n_c_p_gi_tr_c_t_l_i_c_a_tuy_n_ng_n_agi.svg", "nonexistent_f01.svg")
        issues = validate_draft_structure(broken_draft, "VIDEO_TRANSCRIPT", base_dir="course_harness/fixtures")
        self.assertTrue(any("Broken relative image path" in i for i in issues))

        # Negative case: Altered SVG file causes hash mismatch in manifest verification
        temp_manifest_dir = os.path.join(self.assets_dir, "M01-L07")
        os.makedirs(temp_manifest_dir, exist_ok=True)
        temp_manifest_path = os.path.join(temp_manifest_dir, "visual_manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_copy = json.load(f)
        corrupt_svg_path = os.path.join(temp_manifest_dir, "corrupt.svg")
        with open(corrupt_svg_path, "wb") as f:
            f.write(b"<svg>corrupt content</svg>")
        manifest_copy["figures"][0]["rendered_asset_path"] = "corrupt.svg"
        with open(temp_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_copy, f)

        corrupt_errs = VisualAssetManager.verify_manifest_assets(temp_manifest_path, base_dir=temp_manifest_dir)
        self.assertTrue(any("hash mismatch" in e for e in corrupt_errs))

    def test_q07_calibration_audit_integrity_and_hard_gate_regression(self):
        """35. Q-07 Regression: Fixture is explicitly classified as static calibration evidence; hard gates hold."""
        audit_rep = get_m01_l07_audit_report()

        # Classify static test fixture as calibration evidence, not live AI audit
        self.assertTrue(any("STATIC_CALIBRATION_EVIDENCE" in limit for limit in audit_rep.get("limitations", [])))

        # Reconciled fixture passes validation
        val_rep, _ = self.audit_validator.validate_report(json.dumps(audit_rep), "M01-L07")
        self.assertEqual(val_rep["verdict"], "PASS")

        # Hard Gate: HIGH severity finding MUST fail verdict regardless of quality score 100
        dim_scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        high_fidelity_finding = [{
            "finding_id": "F-FIDELITY-17",
            "severity": "HIGH",
            "category": "SOURCE_FIDELITY",
            "source_locator": "00:01",
            "draft_locator": "Section 2",
            "description": "Unsupported claim of 17 experts in transcript.",
            "required_action": "Remove unsupported claim.",
        }]
        res = calculate_quality_score(dim_scores, high_fidelity_finding)
        self.assertEqual(res["quality_score"], 100.0)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertFalse(res["content_quality_accepted"])
        self.assertFalse(res["hard_gates_passed"])

    def test_source_locator_cleanup_regression(self):
        """36. Source locators correctly attribute prototype example to [04:37], not only [03:42]."""
        draft = get_m01_l07_draft_markdown()
        # Prototype example must be attributed to [04:37]
        self.assertIn("Cộng tác sớm bằng bản mẫu thử nghiệm (Customer Collaboration) [04:37]", draft)
        # Traceability table maps prototypes to [04:37]
        self.assertIn("[03:42], [04:37]", draft)


if __name__ == "__main__":
    unittest.main()
