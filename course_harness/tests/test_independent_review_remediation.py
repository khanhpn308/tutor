"""Deterministic Regression Tests for Course Harness v1 Independent Review Remediation R1.

Covers:
- F-01 (HIGH): SHA-256 calculation on exact bytes written to .mmd files.
- F-02 (MEDIUM): Elimination of machine-facing enums from student-facing Markdown.
- F-03 (MEDIUM): Rejection of default 100% score for missing mandatory quality dimensions.
- F-04 (MEDIUM): Canonical path traversal, absolute path, and symlink escape defenses.
"""

import hashlib
import json
import os
import shutil
import tempfile
import unittest

from course_harness.fixtures.m01_l07_calibration import (
    get_m01_l07_draft_markdown,
    get_m01_l07_visual_manifest,
)
from course_harness.validator import (
    AuditValidator,
    ValidationError,
    validate_draft_structure,
    validate_student_facing_cleanliness,
    validate_visual_pedagogy,
)
from course_harness.visual import (
    QUALITY_RUBRIC_VERSION,
    VisualAssetManager,
    calculate_quality_score,
    validate_figure_properties,
)


class TestIndependentReviewRemediation(unittest.TestCase):
    """Regression test suite for Independent Review Findings F-01 through F-04."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.assets_dir = os.path.join(self.test_dir, "assets")
        os.makedirs(self.assets_dir, exist_ok=True)
        self.audit_validator = AuditValidator("course_harness/schemas/audit.schema.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # F-01: SHA-256 mismatch regression test
    # -------------------------------------------------------------------------
    def test_f01_generated_mmd_sha_matches_disk_bytes_and_verifies(self):
        """F-01: process_figures_for_lesson computes SHA-256 on exact written bytes and passes verify_manifest_assets."""
        asset_mgr = VisualAssetManager(self.assets_dir, mmdc_binary="/nonexistent/bin/mmdc")
        lesson_id = "M01-TEST"
        figures = [
            {
                "figure_id": "F01",
                "title": "Diagram Test Title",
                "visual_type": "FLOWCHART",
                "educational_purpose": "Mục đích giáo dục kiểm thử băm SHA.",
                "related_learning_objective": "Kiểm thử băm SHA.",
                "source_locators": ["01:00"],
                "provenance_class": "PEDAGOGICAL_RECONSTRUCTION",
                "alt_text": "Mô tả trực quan có độ dài trên mười ký tự.",
                "caption": "Hình F01: Chú thích sơ đồ kiểm thử.",
                "mermaid_code": "flowchart TD\n    A[Bắt đầu] --> B[Kết thúc]",
            }
        ]

        proc_figs, manifest_path, _ = asset_mgr.process_figures_for_lesson(lesson_id, figures)
        self.assertEqual(len(proc_figs), 1)

        # 1. Read file directly from disk and check hash
        spec_rel = proc_figs[0]["source_spec_path"]
        spec_full = os.path.join(self.assets_dir, "..", spec_rel)
        if not os.path.exists(spec_full):
            # Try direct relative to assets_dir parent
            spec_full = os.path.join(self.test_dir, spec_rel)
        self.assertTrue(os.path.exists(spec_full), f"MMD file not found at {spec_full}")

        with open(spec_full, "rb") as sf:
            disk_bytes = sf.read()
        disk_sha = hashlib.sha256(disk_bytes).hexdigest()

        # The manifest must record the exact hash of the disk file
        expected_sha = proc_figs[0]["source_spec_sha256"]
        self.assertEqual(
            expected_sha,
            disk_sha,
            f"F-01 Regression: Manifest source_spec_sha256 ({expected_sha}) does not match disk bytes SHA ({disk_sha})",
        )

        # 2. verify_manifest_assets must succeed with zero errors
        verify_errors = VisualAssetManager.verify_manifest_assets(
            manifest_path=manifest_path,
            base_dir=self.test_dir,
        )
        self.assertEqual(
            verify_errors,
            [],
            f"F-01 Regression: verify_manifest_assets failed on freshly generated manifest: {verify_errors}",
        )

    # -------------------------------------------------------------------------
    # F-02: Student-facing Markdown machine enums regression test
    # -------------------------------------------------------------------------
    def test_f02_student_facing_cleanliness_rejects_machine_enums(self):
        """F-02: Validator rejects student-facing Markdown containing internal machine enums."""
        # Negative test 1: draft exposing AI_GENERATED_EXAMPLE in heading or text
        bad_draft_1 = (
            "# Tiêu đề bài học\n\n"
            "## 1. Mục tiêu\nNắm vững kiến thức [00:01].\n\n"
            "## 2. Lý thuyết\nNội dung chính [01:00].\n\n"
            "## 3. Tóm tắt\nTóm tắt cốt lõi.\n\n"
            "## 4. Nguồn đối chiếu\nĐối chiếu [00:01].\n\n"
            "### 4.2. Tình huống giả định minh họa (AI_GENERATED_EXAMPLE)\n"
            "> **Ghi chú sư phạm (AI_GENERATED_EXAMPLE):** Tình huống sau đây...\n"
        )
        issues_1 = validate_student_facing_cleanliness(bad_draft_1)
        self.assertTrue(
            any("machine" in i.lower() or "ai_generated_example" in i.lower() for i in issues_1),
            f"F-02 Regression: validate_student_facing_cleanliness failed to flag AI_GENERATED_EXAMPLE: {issues_1}",
        )

        # Negative test 2: draft exposing internal pipeline enums like PEDAGOGICAL_RECONSTRUCTION or SOURCE_DERIVED
        bad_draft_2 = (
            "# Tiêu đề\n\n"
            "Văn bản cho sinh viên chứa mã enum PEDAGOGICAL_RECONSTRUCTION ở thân bài.\n"
        )
        issues_2 = validate_student_facing_cleanliness(bad_draft_2)
        self.assertTrue(
            any("pedagogical_reconstruction" in i.lower() or "machine" in i.lower() for i in issues_2),
            f"F-02 Regression: validate_student_facing_cleanliness failed to flag PEDAGOGICAL_RECONSTRUCTION: {issues_2}",
        )

        # Positive test: Clean student-facing text using natural pedagogical language
        clean_draft = (
            "# Tiêu đề bài học\n\n"
            "## 1. Mục tiêu\nNắm vững kiến thức [00:01].\n\n"
            "## 2. Lý thuyết\nNội dung chính [01:00].\n\n"
            "## 3. Tóm tắt\nTóm tắt cốt lõi.\n\n"
            "## 4. Nguồn đối chiếu\nĐối chiếu [00:01].\n\n"
            "### 4.2. Tình huống giả định minh họa\n"
            "> **Ghi chú sư phạm (Tình huống giả định):** Tình huống sau đây được xây dựng nhằm minh họa...\n"
        )
        issues_clean = validate_student_facing_cleanliness(clean_draft)
        self.assertEqual(issues_clean, [])

    # -------------------------------------------------------------------------
    # F-03: Incomplete quality dimensions regression test
    # -------------------------------------------------------------------------
    def test_f03_missing_mandatory_dimension_does_not_score_100_percent(self):
        """F-03: calculate_quality_score does not normalize missing mandatory dimensions to 100% PASS."""
        # Incomplete report providing only 1 dimension
        single_dim_scores = {
            "SOURCE_FIDELITY": "MET",
        }
        res = calculate_quality_score(single_dim_scores, [])

        self.assertFalse(
            res["hard_gates_passed"],
            "F-03 Regression: hard_gates_passed should be False when mandatory dimensions are omitted",
        )
        self.assertEqual(
            res["verdict"],
            "FAIL",
            "F-03 Regression: verdict should be FAIL when mandatory dimensions are omitted",
        )
        self.assertLess(
            res["quality_score"],
            90.0,
            f"F-03 Regression: quality_score should be < 90.0 (got {res['quality_score']}) when mandatory dimensions are missing",
        )

        # Audit validator rejects PASS verdict with missing mandatory dimensions
        audit_rep = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "summary": "Incomplete audit report.",
            "dimension_scores": single_dim_scores,
            "findings": [],
            "limitations": ["Incomplete dimensions test."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.audit_validator.validate_report(audit_rep, "M01-L07")
        self.assertTrue(
            "threshold" in str(ctx.exception) or "missing" in str(ctx.exception).lower(),
            f"Expected ValidationError mentioning threshold or missing dimensions, got: {ctx.exception}",
        )

    def test_f03_preserves_valid_exemptions_and_legacy_backward_compatibility(self):
        """F-03: Preserves NOT_APPLICABLE exemption for QUIZ/GLOSSARY/LOCKED and legacy 7-dimension reports."""
        # 1. QUIZ exemption
        quiz_res = calculate_quality_score(
            {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            [],
            lesson_type="QUIZ",
        )
        self.assertEqual(quiz_res["quality_score"], 100.0)
        self.assertEqual(quiz_res["verdict"], "PASS")

        # 2. Legacy 7-dimension audit report backward compatibility
        legacy_scores = {
            "SOURCE_FIDELITY": "MET",
            "COMPLETENESS": "MET",
            "TECHNICAL_ACCURACY": "MET",
            "TERMINOLOGY": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "STRUCTURE": "MET",
            "TRACEABILITY": "MET",
        }
        legacy_res = calculate_quality_score(legacy_scores, [])
        self.assertEqual(legacy_res["quality_score"], 100.0)
        self.assertEqual(legacy_res["verdict"], "PASS")

    # -------------------------------------------------------------------------
    # F-04: Path traversal and symlink escape regression test
    # -------------------------------------------------------------------------
    def test_f04_path_traversal_and_symlink_escape_rejection(self):
        """F-04: Traversal (including <= 2 dots), absolute paths, and symlink escapes are rejected."""
        # 1. Image path traversal with 1 or 2 dot-dots must be specifically flagged as traversal
        draft_with_traversal = (
            "# Bài học\n\n"
            "![Sơ đồ minh họa](assets/../secret.svg)\n"
        )
        issues = validate_visual_pedagogy(draft_with_traversal, "VIDEO_TRANSCRIPT")
        self.assertTrue(
            any("traversal" in i.lower() for i in issues),
            f"F-04 Regression: validator failed to detect '..' path traversal in image reference: {issues}",
        )

        # 2. Absolute path in figure property must be rejected
        abs_fig = {
            "figure_id": "F01",
            "title": "Absolute Path Test",
            "visual_type": "CONCEPT_MAP",
            "educational_purpose": "Kiểm thử đường dẫn tuyệt đối.",
            "related_learning_objective": "Học tập.",
            "source_locators": ["00:01"],
            "provenance_class": "SOURCE_DERIVED",
            "alt_text": "Mô tả trực quan chi tiết trên mười ký tự.",
            "caption": "Hình F01: Chú thích sơ đồ.",
            "source_spec_path": "/etc/passwd",
        }
        errs_abs = validate_figure_properties(abs_fig)
        self.assertTrue(
            any("must be relative" in e.lower() or "absolute" in e.lower() for e in errs_abs),
            f"F-04 Regression: validate_figure_properties allowed absolute path: {errs_abs}",
        )

        # 3. Symlink escape detection in verify_manifest_assets
        # Create a file outside the assets directory
        outside_target = os.path.join(self.test_dir, "secret.mmd")
        with open(outside_target, "w", encoding="utf-8") as f:
            f.write("graph TD\nA-->B\n")
        outside_sha = hashlib.sha256(b"graph TD\nA-->B\n").hexdigest()

        # Place symlink inside the assets directory
        lesson_assets = os.path.join(self.assets_dir, "M01-ESCAPE")
        os.makedirs(lesson_assets, exist_ok=True)
        symlink_path = os.path.join(lesson_assets, "escaped_link.mmd")
        try:
            os.symlink(outside_target, symlink_path)
        except OSError:
            self.skipTest("Symlinks not supported in environment")

        manifest_path = os.path.join(lesson_assets, "visual_manifest.json")
        manifest_data = {
            "lesson_id": "M01-ESCAPE",
            "figures": [
                {
                    "figure_id": "F01",
                    "source_spec_path": "M01-ESCAPE/escaped_link.mmd",
                    "source_spec_sha256": outside_sha,
                }
            ],
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f)

        # verify_manifest_assets with base_dir=self.assets_dir
        # Since escaped_link.mmd points to outside_target (outside self.assets_dir),
        # verify_manifest_assets must block/reject it as symlink escape or unsafe path!
        symlink_errs = VisualAssetManager.verify_manifest_assets(
            manifest_path=manifest_path,
            base_dir=self.assets_dir,
        )
        self.assertTrue(
            any("symlink" in e.lower() or "escape" in e.lower() or "traversal" in e.lower() or "unsafe" in e.lower() for e in symlink_errs),
            f"F-04 Regression: verify_manifest_assets allowed symlink escaping base_dir: {symlink_errs}",
        )


if __name__ == "__main__":
    unittest.main()
