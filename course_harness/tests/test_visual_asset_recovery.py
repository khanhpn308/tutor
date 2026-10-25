"""Focused unit tests for visual asset path recovery and normalization.

Covers:
1. Mismatched Worker English slug vs rendered Vietnamese slug.
2. F01/F02 correct mapping by figure_id.
3. Broken image path rejection.
4. Publication-relative link resolution (root and modules layout).
5. Existing valid figure hashes remain intact.
6. Idempotent asset normalization.
7. Advancement to Auditor prevented when blocking draft-integrity errors remain.
"""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

from course_harness.run import CourseHarnessController
from course_harness.validator import (
    classify_draft_issues,
    validate_draft_structure,
)
from course_harness.visual import (
    VisualAssetManager,
    calculate_sha256_bytes,
    normalize_markdown_asset_paths,
    validate_figure_semantic_binding,
)


class TestVisualAssetRecovery(unittest.TestCase):
    """Test suite covering visual asset path recovery, normalization, and safety gates."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.assets_dir = os.path.join(self.test_dir, "assets", "M01-L01")
        self.modules_dir = os.path.join(self.test_dir, "modules", "M01")
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.modules_dir, exist_ok=True)

        # Stage assets symlink in modules_dir for publication layout
        os.symlink("../../assets", os.path.join(self.modules_dir, "assets"))

        # Create dummy SVGs with distinct content
        self.f01_svg_rel = "assets/M01-L01/F01_l_tr_nh_chuy_n_ti_p_n_ng_l_c_qu_n_tr_d_n.svg"
        self.f02_svg_rel = "assets/M01-L01/F02_m_h_nh_chi_c_agile_v_c_u_tr_c_kh_a_h_c.svg"

        self.f01_svg_path = os.path.join(self.test_dir, self.f01_svg_rel)
        self.f02_svg_path = os.path.join(self.test_dir, self.f02_svg_rel)

        f01_bytes = b"<svg xmlns='http://www.w3.org/2000/svg'><text>F01 Content</text></svg>"
        f02_bytes = b"<svg xmlns='http://www.w3.org/2000/svg'><text>F02 Content</text></svg>"

        with open(self.f01_svg_path, "wb") as f:
            f.write(f01_bytes)
        with open(self.f02_svg_path, "wb") as f:
            f.write(f02_bytes)

        self.f01_sha = calculate_sha256_bytes(f01_bytes)
        self.f02_sha = calculate_sha256_bytes(f02_bytes)

        self.manifest_data = {
            "lesson_id": "M01-L01",
            "total_figures": 2,
            "figures": [
                {
                    "figure_id": "F01",
                    "title": "Lộ trình Chuyển tiếp Năng lực Quản trị Dự án",
                    "rendered_asset_path": self.f01_svg_rel,
                    "rendered_asset_sha256": self.f01_sha,
                },
                {
                    "figure_id": "F02",
                    "title": 'Mô hình "Chiếc ô Agile" và Cấu trúc Khóa học',
                    "rendered_asset_path": self.f02_svg_rel,
                    "rendered_asset_sha256": self.f02_sha,
                },
            ],
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mismatched_worker_english_slug_vs_rendered_vietnamese_slug(self):
        """Worker draft referencing English filename slugs is normalized to rendered Vietnamese slugs."""
        raw_worker_markdown = (
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Lộ trình Chuyển tiếp\n\n"
            "![Hình F01: Mô tả F01](assets/M01-L01/F01_project_management_learning_path.svg)\n\n"
            "```mermaid\nflowchart TD\nA --> B\n```\n"
            "<!-- FIGURE_END: F01 -->\n\n"
            "<!-- FIGURE_START: F02 -->\n"
            "#### Hình F02: Mô hình Chiếc ô Agile\n\n"
            "![Hình F02: Mô tả F02](assets/M01-L01/F02_agile_umbrella_model.svg)\n\n"
            "```mermaid\nflowchart TD\nC --> D\n```\n"
            "<!-- FIGURE_END: F02 -->\n"
        )

        normalized = normalize_markdown_asset_paths(raw_worker_markdown, self.manifest_data)

        self.assertNotIn("F01_project_management_learning_path.svg", normalized)
        self.assertNotIn("F02_agile_umbrella_model.svg", normalized)
        self.assertIn(self.f01_svg_rel, normalized)
        self.assertIn(self.f02_svg_rel, normalized)

    def test_f01_f02_correct_mapping(self):
        """Figures are bound strictly by figure_id, even if reordered or renamed in the draft."""
        # Draft with reversed order: F02 before F01
        reversed_order_markdown = (
            "<!-- FIGURE_START: F02 -->\n"
            "#### Hình F02: Title F02\n\n"
            "![Hình F02: Alt text for F02](assets/M01-L01/F02_arbitrary_english_slug.svg)\n\n"
            "```mermaid\nflowchart TD\nC --> D\n```\n"
            "<!-- FIGURE_END: F02 -->\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Title F01\n\n"
            "![Hình F01: Alt text for F01](assets/M01-L01/F01_arbitrary_english_slug.svg)\n\n"
            "```mermaid\nflowchart TD\nA --> B\n```\n"
            "<!-- FIGURE_END: F01 -->\n"
        )

        normalized = normalize_markdown_asset_paths(reversed_order_markdown, self.manifest_data)

        # F02 must resolve to F02's path, F01 to F01's path
        self.assertIn(f"![Hình F02: Alt text for F02]({self.f02_svg_rel})", normalized)
        self.assertIn(f"![Hình F01: Alt text for F01]({self.f01_svg_rel})", normalized)

    def test_broken_image_path_rejection(self):
        """Broken or nonexistent relative image paths are detected and flagged as blocking issues."""
        broken_markdown = (
            "# Bài học M01-L01\n\n"
            "## 1. Mục tiêu bài học\n- Mục tiêu 1\n\n"
            "## 2. Nội dung lý thuyết\n\n"
            "![Hình F01: Sơ đồ](assets/M01-L01/F01_project_management_learning_path.svg)\n\n"
            "## 3. Tóm tắt cốt lõi\n- Tóm tắt\n\n"
            "## 4. Nguồn đối chiếu\n| Mục | Nguồn |\n"
        )

        issues = validate_draft_structure(
            broken_markdown, "VIDEO_TRANSCRIPT", lesson_id="M01-L01", base_dir=self.test_dir
        )
        blocking, warnings = classify_draft_issues(issues)

        self.assertTrue(any("Broken relative image path" in b for b in blocking))
        self.assertTrue(any("F01_project_management_learning_path.svg" in b for b in blocking))

    def test_publication_relative_link_resolution(self):
        """Normalized image paths resolve cleanly from both course root and staged modules publication layout."""
        valid_markdown = (
            "# Bài học M01-L01\n\n"
            "## 1. Mục tiêu bài học\n- Mục tiêu 1\n\n"
            "## 2. Nội dung lý thuyết\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Lộ trình Chuyển tiếp\n\n"
            f"![Hình F01: Sơ đồ luồng tiến trình chuyển tiếp]({self.f01_svg_rel})\n\n"
            "```mermaid\nflowchart TD\nA --> B\n```\n"
            "<!-- FIGURE_END: F01 -->\n\n"
            "<!-- FIGURE_START: F02 -->\n"
            "#### Hình F02: Mô hình Chiếc ô Agile\n\n"
            f"![Hình F02: Mô hình chiếc ô Agile và khung làm việc]({self.f02_svg_rel})\n\n"
            "```mermaid\nflowchart TD\nC --> D\n```\n"
            "<!-- FIGURE_END: F02 -->\n\n"
            "## 3. Tóm tắt cốt lõi\n- Tóm tắt\n\n"
            "## 4. Nguồn đối chiếu\n| Mục | Nguồn |\n"
        )

        # 1. From course root
        issues_root = validate_draft_structure(
            valid_markdown, "VIDEO_TRANSCRIPT", lesson_id="M01-L01", base_dir=self.test_dir
        )
        blocking_root, _ = classify_draft_issues(issues_root)
        self.assertEqual(blocking_root, [])

        # 2. From publication module directory (modules/M01)
        issues_mod = validate_draft_structure(
            valid_markdown, "VIDEO_TRANSCRIPT", lesson_id="M01-L01", base_dir=self.modules_dir
        )
        blocking_mod, _ = classify_draft_issues(issues_mod)
        self.assertEqual(blocking_mod, [])

    def test_existing_valid_figure_hashes_remain_intact(self):
        """Asset normalization preserves original rendered SVG files and their manifest hashes intact."""
        real_manifest_path = "generated_course/Agile_Project_Management/assets/M01-L01/visual_manifest.json"
        course_dir = "generated_course/Agile_Project_Management"

        self.assertTrue(os.path.exists(real_manifest_path))

        # Verify manifest assets against disk
        errors = VisualAssetManager.verify_manifest_assets(real_manifest_path, base_dir=course_dir)
        self.assertEqual(errors, [], f"Manifest asset verification failed: {errors}")

        with open(real_manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for fig in manifest["figures"]:
            rendered_rel = fig["rendered_asset_path"]
            expected_sha = fig["rendered_asset_sha256"]
            full_path = os.path.join(course_dir, rendered_rel)
            self.assertTrue(os.path.exists(full_path))
            with open(full_path, "rb") as f:
                actual_sha = calculate_sha256_bytes(f.read())
            self.assertEqual(actual_sha, expected_sha)

    def test_idempotent_asset_normalization(self):
        """Repeatedly normalizing markdown is strictly idempotent."""
        sample_markdown = (
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Title\n\n"
            "![Hình F01: Alt text](assets/M01-L01/F01_unnormalized_slug.svg)\n\n"
            "```mermaid\nflowchart TD\nA --> B\n```\n"
            "<!-- FIGURE_END: F01 -->\n"
        )

        first_pass = normalize_markdown_asset_paths(sample_markdown, self.manifest_data)
        second_pass = normalize_markdown_asset_paths(first_pass, self.manifest_data)
        third_pass = normalize_markdown_asset_paths(second_pass, self.manifest_data)

        self.assertEqual(first_pass, second_pass)
        self.assertEqual(second_pass, third_pass)

    def test_advancement_to_auditor_prevented_when_blocking_draft_errors(self):
        """Controller blocks advancement to Auditor and transitions to NEEDS_HUMAN_REVIEW on broken drafts."""
        config_path = os.path.join(self.test_dir, "config.yaml")
        manifest_path = os.path.join(self.test_dir, "manifest.json")
        source_dir = os.path.join(self.test_dir, "sources")
        drafts_dir = os.path.join(self.test_dir, "drafts")
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(drafts_dir, exist_ok=True)

        raw_rel = "Module_01/01_intro.md"
        raw_full = os.path.join(source_dir, raw_rel)
        os.makedirs(os.path.dirname(raw_full), exist_ok=True)
        with open(raw_full, "w", encoding="utf-8") as f:
            f.write("# Introduction Source\n")

        import hashlib
        raw_sha = hashlib.sha256(b"# Introduction Source\n").hexdigest()

        manifest_data = {
            "course_id": "Agile_Project_Management",
            "total_modules": 1,
            "total_lessons": 1,
            "modules": {"M01": {"title": "Module 1", "lesson_count": 1, "lesson_ids": ["M01-L01"]}},
            "lessons": {
                "M01-L01": {
                    "lesson_id": "M01-L01",
                    "module_id": "M01",
                    "title": "Introduction to Course 5",
                    "relative_path": raw_rel,
                    "source_type": "VIDEO_TRANSCRIPT",
                    "status": "AVAILABLE",
                    "source_sha256": raw_sha,
                }
            },
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f)

        config_data = {
            "models": {
                "worker": {"model": "gemini-3.8-flash-high", "effort": "high"},
                "auditor": {"model": "gemini-3.8-flash-high", "effort": "high"},
                "repair": {"model": "gemini-3.8-flash-high", "effort": "high"},
            },
            "workflow": {"max_repair_rounds": 2},
            "paths": {
                "course_id": "Agile_Project_Management",
                "source_dir": source_dir,
                "output_dir": self.test_dir,
                "manifest_path": manifest_path,
                "schema_path": "course_harness/schemas/audit.schema.json",
                "prompts_dir": "course_harness/prompts",
            },
        }
        import yaml
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        controller = CourseHarnessController(config_path, mode_override="mock")

        # Mock worker to return a draft with broken image path
        broken_draft = (
            "# Bài học M01-L01\n\n"
            "## 1. Mục tiêu bài học\n- Mục tiêu\n\n"
            "## 2. Nội dung lý thuyết\n\n"
            "![Hình F01: Mô tả](assets/M01-L01/F01_nonexistent_broken.svg)\n\n"
            "## 3. Tóm tắt cốt lõi\n- Tóm tắt\n\n"
            "## 4. Nguồn đối chiếu\n| Mục | Nguồn |\n"
        )
        draft_file = os.path.join(drafts_dir, "M01-L01_draft_v1.md")
        with open(draft_file, "w", encoding="utf-8") as f:
            f.write(broken_draft)

        controller._run_worker_draft = MagicMock(return_value=(broken_draft, draft_file, {}))
        controller._run_auditor = MagicMock()

        result = controller.process_lesson("M01-L01", reset=True)

        # Auditor must NEVER be called
        controller._run_auditor.assert_not_called()
        self.assertEqual(result["status"], "NEEDS_HUMAN_REVIEW")
        self.assertIn("DRAFT_INTEGRITY_ERROR", result.get("error_category", ""))


if __name__ == "__main__":
    unittest.main()
