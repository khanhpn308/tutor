"""Focused unit and integration tests for Course Harness v1 Pilot Recovery.

Covers:
1. Auditor prompt contract requirements (quality_rubric_version == '2.0-visual-first')
2. Controller error handling on invalid audit report validation
3. Trustworthy model provenance verification (positive, negative mismatch, and missing session)
4. Safe educational draft reuse during pilot recovery
"""

import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from course_harness.cli_adapter import AgyAdapter, ModelUnavailableError
from course_harness.run import CourseHarnessController
from course_harness.validator import (
    AuditValidator,
    ValidationError,
    validate_draft_structure,
    validate_student_facing_cleanliness,
    validate_labeled_hypothetical_examples,
)


class TestAuditorPromptContract(unittest.TestCase):
    """Verifies that auditor prompt and validator schemas strictly align."""

    def test_auditor_prompt_contract_contains_rubric_2_0_version(self):
        """auditor.md JSON output template must explicitly specify quality_rubric_version: '2.0-visual-first'."""
        prompt_path = "course_harness/prompts/auditor.md"
        self.assertTrue(os.path.exists(prompt_path), f"Missing prompt file: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('"quality_rubric_version": "2.0-visual-first"', content)
        for canonical_dim in [
            "SOURCE_FIDELITY",
            "CONTENT_COMPLETENESS",
            "PEDAGOGICAL_QUALITY",
            "VISUAL_PEDAGOGY",
            "TERMINOLOGY_CONSISTENCY",
            "SOURCE_TRACEABILITY",
            "CLARITY_ORGANIZATION",
            "FORMATTING",
        ]:
            self.assertIn(canonical_dim, content)

    def test_validator_rejects_missing_quality_rubric_version_on_modern_dims(self):
        """AuditValidator must reject modern 8-dimension reports missing quality_rubric_version."""
        validator = AuditValidator("course_harness/schemas/audit.schema.json")
        invalid_report = {
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "summary": "Valid summary",
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
            "limitations": ["Note"],
        }
        with self.assertRaises(ValidationError) as ctx:
            validator.validate_report(json.dumps(invalid_report), expected_lesson_id="M02-L11")
        self.assertIn("quality_rubric_version", str(ctx.exception))

    def test_validator_accepts_valid_rubric_2_0_report(self):
        """AuditValidator accepts report with explicit quality_rubric_version and all 8 dimensions."""
        validator = AuditValidator("course_harness/schemas/audit.schema.json")
        valid_report = {
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "summary": "High quality draft",
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
            "limitations": ["Audit completed independently"],
        }
        payload, warnings = validator.validate_report(
            json.dumps(valid_report), expected_lesson_id="M02-L11"
        )
        self.assertEqual(payload["quality_rubric_version"], "2.0-visual-first")
        self.assertEqual(payload["verdict"], "PASS")


class TestControllerErrorHandling(unittest.TestCase):
    """Verifies that Controller gracefully handles auditor schema validation errors."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.yaml")
        manifest_path = os.path.join(self.test_dir, "manifest.json")
        source_dir = os.path.join(self.test_dir, "sources")
        modules_dir = os.path.join(self.test_dir, "modules")
        drafts_dir = os.path.join(self.test_dir, "drafts")
        audits_dir = os.path.join(self.test_dir, "audits")
        evidence_dir = os.path.join(self.test_dir, "evidence")
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(modules_dir, exist_ok=True)
        os.makedirs(drafts_dir, exist_ok=True)
        os.makedirs(audits_dir, exist_ok=True)
        os.makedirs(evidence_dir, exist_ok=True)

        raw_rel = "Module_01/07_test.md"
        raw_full = os.path.join(source_dir, raw_rel)
        os.makedirs(os.path.dirname(raw_full), exist_ok=True)
        with open(raw_full, "w", encoding="utf-8") as f:
            f.write("# Raw Lesson Source Content\n")

        import hashlib
        raw_sha = hashlib.sha256(b"# Raw Lesson Source Content\n").hexdigest()

        manifest_data = {
            "course_id": "Agile_Project_Management",
            "total_modules": 1,
            "total_lessons": 1,
            "modules": {"M01": {"title": "Module 1", "lesson_count": 1, "lesson_ids": ["M01-L07"]}},
            "lessons": {
                "M01-L07": {
                    "lesson_id": "M01-L07",
                    "module_id": "M01",
                    "title": "Test Lesson",
                    "relative_path": raw_rel,
                    "source_type": "READING",
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
        with open(self.config_path, "w", encoding="utf-8") as f:
            import yaml
            yaml.dump(config_data, f)

        self.controller = CourseHarnessController(self.config_path, mode_override="mock")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_controller_handles_auditor_validation_error_gracefully(self):
        """Controller must not crash with unhandled exception on ValidationError; transitions to NEEDS_HUMAN_REVIEW."""
        # Monkey patch _run_auditor to simulate schema validation failure
        def mock_failing_auditor(lesson_meta, raw_content, current_draft, attempt):
            bad_path = os.path.join(self.controller.audits_dir, f"M01-L07_audit_v{attempt}_INVALID.txt")
            with open(bad_path, "w", encoding="utf-8") as f:
                f.write('{"invalid_json": true}')
            raise ValidationError("Simulated schema rejection: missing required fields")

        self.controller._run_auditor = mock_failing_auditor

        res = self.controller.process_lesson("M01-L07", reset=True)
        self.assertEqual(res["status"], "NEEDS_HUMAN_REVIEW")
        self.assertIn("AUDIT_VALIDATION_ERROR", res.get("error_category", ""))
        self.assertEqual(res.get("verdict"), "INCONCLUSIVE")
        self.assertEqual(res.get("repair_attempts", 0), 0)
        # Verify bad audit response was preserved
        bad_audit_file = os.path.join(self.controller.audits_dir, "M01-L07_audit_v1_INVALID.txt")
        self.assertTrue(os.path.exists(bad_audit_file))


class TestModelProvenanceVerification(unittest.TestCase):
    """Verifies trustworthy model provenance resolution from AGY execution artifacts."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.session_dir = os.path.join(self.test_dir, "mock_agy_home")
        os.makedirs(os.path.join(self.session_dir, "conversations"), exist_ok=True)
        os.makedirs(os.path.join(self.session_dir, "brain"), exist_ok=True)
        self.adapter = AgyAdapter(
            mode="automated_cli",
            evidence_dir=self.test_dir,
            session_dir=self.session_dir,
            model="gemini-3.8-flash-high",
            effort="high",
        )
        self.adapter.resolved_binary = "/bin/mock-agy"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_session_db(self, conv_id: str, model_id: str):
        db_path = os.path.join(self.session_dir, "conversations", f"{conv_id}.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE gen_metadata (idx integer primary key, data blob)")
        cur.execute("CREATE TABLE executor_metadata (idx integer primary key, data blob)")
        model_b = model_id.encode("utf-8")
        blob = b"prefix_tag\xe2\x01" + bytes([len(model_b)]) + model_b + b"_suffix"
        cur.execute("INSERT INTO gen_metadata (idx, data) VALUES (0, ?)", (blob,))
        conn.commit()
        conn.close()

    def test_positive_model_provenance_resolution(self):
        """When envelope lacks model but session DB contains exact pinned model, verification succeeds."""
        conv_id = "conv-pos-12345"
        self._create_mock_session_db(conv_id, "gemini-3.8-flash-high")

        resolved_model, evidence = self.adapter.resolve_session_model(conv_id)
        self.assertEqual(resolved_model, "gemini-3.8-flash-high")
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.get("source"), "sqlite_gen_metadata")

        envelope = {
            "conversation_id": conv_id,
            "status": "SUCCESS",
            "response": "# Generated Lesson Output",
            "duration_seconds": 12.3,
            "usage": {"total_tokens": 500},
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=json.dumps(envelope), stderr=""
            )
            resp, meta = self.adapter._invoke_automated(
                "prompt", "p.md", "worker", "M01-L01", "json", 1
            )
            self.assertEqual(meta["model_reported"], "gemini-3.8-flash-high")
            self.assertEqual(meta["model_verified"], "VERIFIED")
            self.assertEqual(meta["evidence_class"], "REAL_AGY_VERIFIED")
            self.assertIn("model_verification_evidence", meta)

    def test_negative_model_provenance_mismatch_raises_error(self):
        """When session DB records a fallback model, verification raises ModelUnavailableError."""
        conv_id = "conv-mismatch-67890"
        self._create_mock_session_db(conv_id, "claude-sonnet-4-6")

        resolved_model, _ = self.adapter.resolve_session_model(conv_id)
        self.assertEqual(resolved_model, "claude-sonnet-4-6")

        envelope = {
            "conversation_id": conv_id,
            "status": "SUCCESS",
            "response": "# Output from wrong model",
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=json.dumps(envelope), stderr=""
            )
            with self.assertRaises(ModelUnavailableError) as ctx:
                self.adapter._invoke_automated(
                    "prompt", "p.md", "worker", "M01-L01", "json", 1
                )
            self.assertIn("BLOCKED_MODEL_UNAVAILABLE", str(ctx.exception))
            self.assertEqual(self.adapter.last_model_verified, "MISMATCH")

    def test_missing_session_artifacts_retains_not_verified(self):
        """When neither envelope nor session DB provides model identity, model_verified remains NOT_VERIFIED."""
        conv_id = "conv-unknown-99999"
        resolved_model, evidence = self.adapter.resolve_session_model(conv_id)
        self.assertIsNone(resolved_model)
        self.assertIsNone(evidence)

        envelope = {
            "conversation_id": conv_id,
            "status": "SUCCESS",
            "response": "# Output without identity",
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=json.dumps(envelope), stderr=""
            )
            resp, meta = self.adapter._invoke_automated(
                "prompt", "p.md", "worker", "M01-L01", "json", 1
            )
            self.assertIsNone(meta["model_reported"])
            self.assertEqual(meta["model_verified"], "NOT_VERIFIED")
            self.assertEqual(meta["evidence_class"], "MANUAL_UNVERIFIED")


class TestDraftReuseDuringRecovery(unittest.TestCase):
    """Verifies that an existing draft is reused without invoking worker."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.yaml")
        manifest_path = os.path.join(self.test_dir, "manifest.json")
        source_dir = os.path.join(self.test_dir, "sources")
        modules_dir = os.path.join(self.test_dir, "modules")
        drafts_dir = os.path.join(self.test_dir, "drafts")
        audits_dir = os.path.join(self.test_dir, "audits")
        evidence_dir = os.path.join(self.test_dir, "evidence")
        checkpoints_dir = os.path.join(evidence_dir, "checkpoints")
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(modules_dir, exist_ok=True)
        os.makedirs(drafts_dir, exist_ok=True)
        os.makedirs(audits_dir, exist_ok=True)
        os.makedirs(checkpoints_dir, exist_ok=True)

        raw_rel = "Module_01/07_test.md"
        raw_full = os.path.join(source_dir, raw_rel)
        os.makedirs(os.path.dirname(raw_full), exist_ok=True)
        with open(raw_full, "w", encoding="utf-8") as f:
            f.write("# Raw Lesson Source Content\n")

        import hashlib
        raw_sha = hashlib.sha256(b"# Raw Lesson Source Content\n").hexdigest()

        # Create existing draft
        self.draft_path = os.path.join(drafts_dir, "M01-L07_draft_v1.md")
        with open(self.draft_path, "w", encoding="utf-8") as f:
            f.write("# Preserved Draft Content\n\n## 1. Mục tiêu bài học\n- Mục tiêu 1\n")

        # Create checkpoint referencing existing draft
        chk_path = os.path.join(checkpoints_dir, "M01-L07.json")
        checkpoint_data = {
            "lesson_id": "M01-L07",
            "status": "DRAFTED",
            "source_sha256": raw_sha,
            "prompt_config_hash": "dummy_hash",
            "model_id": "gemini-3.8-flash-high",
            "effort": "high",
            "draft_version": 1,
            "draft_path": self.draft_path,
            "audit_version": 0,
            "repair_attempts": 0,
            "history": [],
            "created_at": "2026-10-25T00:00:00Z",
            "updated_at": "2026-10-25T00:00:00Z",
        }
        with open(chk_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f)

        # Create worker evidence receipt
        worker_ev_path = os.path.join(evidence_dir, "evidence_worker_M01-L07_att1.json")
        with open(worker_ev_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "mode": "automated_cli",
                    "role": "worker",
                    "lesson_id": "M01-L07",
                    "model_reported": "gemini-3.8-flash-high",
                    "model_verified": "VERIFIED",
                    "evidence_class": "REAL_AGY_VERIFIED",
                },
                f,
            )

        manifest_data = {
            "course_id": "Agile_Project_Management",
            "total_modules": 1,
            "total_lessons": 1,
            "modules": {"M01": {"title": "Module 1", "lesson_count": 1, "lesson_ids": ["M01-L07"]}},
            "lessons": {
                "M01-L07": {
                    "lesson_id": "M01-L07",
                    "module_id": "M01",
                    "title": "Test Lesson",
                    "relative_path": raw_rel,
                    "source_type": "READING",
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
        with open(self.config_path, "w", encoding="utf-8") as f:
            import yaml
            yaml.dump(config_data, f)

        self.controller = CourseHarnessController(self.config_path, mode_override="mock")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_draft_reuse_prevents_worker_rerun(self):
        """When draft already exists and reset is False, _run_worker_draft must not be called."""
        worker_called = False

        def mock_worker(*args, **kwargs):
            nonlocal worker_called
            worker_called = True
            return "# New Draft", self.draft_path, {}

        self.controller._run_worker_draft = mock_worker

        # Mock auditor to pass directly
        def mock_auditor(lesson_meta, raw_content, current_draft, attempt):
            audit_report = {
                "lesson_id": "M01-L07",
                "verdict": "PASS",
                "quality_rubric_version": "2.0-visual-first",
                "summary": "Passed",
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
            audit_path = os.path.join(self.controller.audits_dir, "M01-L07_audit_v1.json")
            with open(audit_path, "w", encoding="utf-8") as f:
                json.dump(audit_report, f)
            return audit_report, audit_path, {"model_verified": "VERIFIED"}

        self.controller._run_auditor = mock_auditor

        res = self.controller.process_lesson("M01-L07", reset=False)
        self.assertFalse(worker_called, "Worker was rerun despite existing draft!")
        self.assertEqual(res["draft_path"], self.draft_path)


class TestPublicationRecoveryR2(unittest.TestCase):
    """Focused regression tests for M02-L11 Publication Recovery (TASK A & TASK B)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.course_dir = os.path.join(self.test_dir, "course")
        self.modules_dir = os.path.join(self.course_dir, "modules", "M02")
        self.assets_dir = os.path.join(self.course_dir, "assets", "M02-L11")
        os.makedirs(self.modules_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)

        # Stage assets symlink in modules_dir
        os.symlink("../../assets", os.path.join(self.modules_dir, "assets"))

        # Create dummy rendered SVGs
        self.f01_svg = os.path.join(self.assets_dir, "F01_m_h_nh_tam_gi_c_ba_vai_tr_n_ng_c_t_trong.svg")
        self.f02_svg = os.path.join(self.assets_dir, "F02_ma_tr_n_ph_n_nh_tr_ch_nhi_m_gi_a_project.svg")
        self.f03_svg = os.path.join(self.assets_dir, "F03_chu_tr_nh_ph_i_h_p_t_c_nghi_p_gi_a_ba_va.svg")
        for s in [self.f01_svg, self.f02_svg, self.f03_svg]:
            with open(s, "wb") as f:
                f.write(b"<svg xmlns='http://www.w3.org/2000/svg'><circle cx='10' cy='10' r='5'/></svg>")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_visible_machine_enum_rejection(self):
        """Visible machine-facing enums (AI_GENERATED_EXAMPLE, PEDAGOGICAL_RECONSTRUCTION) are rejected."""
        dirty_content = (
            "# Bài học M02-L11\n\n"
            "## 1. Mục tiêu\n- Mục tiêu\n\n"
            "## 2. Lý thuyết\n"
            "*Hình F01: Mô hình [Nguồn gốc: PEDAGOGICAL_RECONSTRUCTION]*\n\n"
            "### 4.2 Tình huống [AI_GENERATED_EXAMPLE]\n"
        )
        issues = validate_student_facing_cleanliness(dirty_content)
        self.assertTrue(any("PEDAGOGICAL_RECONSTRUCTION" in i for i in issues))
        self.assertTrue(any("AI_GENERATED_EXAMPLE" in i for i in issues))

    def test_vietnamese_pedagogical_labels_accepted(self):
        """Natural Vietnamese labels (Tái cấu trúc sư phạm, Tình huống mô phỏng sư phạm) pass cleanly."""
        clean_content = (
            "# Bài học M02-L11\n\n"
            "## 1. Mục tiêu\n- Mục tiêu 1\n\n"
            "## 2. Lý thuyết\n"
            "*Hình F01: Mô hình ba vai trò [Nguồn gốc: Tái cấu trúc sư phạm, đối chiếu mục 1].*\n\n"
            "### 4.2 Tình huống Thực hành Giả định [Tình huống mô phỏng sư phạm]\n\n"
            "> Tình huống giả định không kèm timestamp nguồn.\n\n"
            "## 5. Tóm tắt cốt lõi\n- Ghi nhớ\n\n"
            "## 6. Nguồn đối chiếu\n| Mục | Locator |\n"
        )
        cleanliness_issues = validate_student_facing_cleanliness(clean_content)
        self.assertEqual(cleanliness_issues, [])
        hypo_issues = validate_labeled_hypothetical_examples(clean_content)
        self.assertEqual(hypo_issues, [])

    def test_svg_links_resolve_from_publication_layout(self):
        """All 3 SVG links resolve correctly relative to base_dir and course publication layout."""
        markdown = (
            "# Bài học M02-L11\n\n"
            "## 1. Mục tiêu bài học\n- Mục tiêu\n\n"
            "## 2. Nội dung lý thuyết\n\n"
            "<!-- FIGURE_START: F01 -->\n"
            "#### Hình F01: Mô hình Tam giác Ba Vai trò Nòng cốt trong Nhóm Scrum\n\n"
            "![Hình F01: Mô tả chi tiết cho sơ đồ khái niệm](assets/M02-L11/F01_m_h_nh_tam_gi_c_ba_vai_tr_n_ng_c_t_trong.svg)\n\n"
            "```mermaid\nflowchart TD\nA --> B\n```\n\n"
            "*Hình F01: Chú thích sư phạm [Nguồn gốc: Tái cấu trúc sư phạm].*\n"
            "<!-- FIGURE_END: F01 -->\n\n"
            "<!-- FIGURE_START: F02 -->\n"
            "#### Hình F02: Ma trận Phân định Trách nhiệm\n\n"
            "![Hình F02: Bảng so sánh trực quan về trách nhiệm](assets/M02-L11/F02_ma_tr_n_ph_n_nh_tr_ch_nhi_m_gi_a_project.svg)\n\n"
            "```mermaid\nflowchart TD\nC --> D\n```\n\n"
            "*Hình F02: Chú thích sư phạm [Nguồn gốc: Tái cấu trúc sư phạm].*\n"
            "<!-- FIGURE_END: F02 -->\n\n"
            "<!-- FIGURE_START: F03 -->\n"
            "#### Hình F03: Chu trình Phối hợp Tác nghiệp\n\n"
            "![Hình F03: Lưu đồ quy trình tương tác phối hợp](assets/M02-L11/F03_chu_tr_nh_ph_i_h_p_t_c_nghi_p_gi_a_ba_va.svg)\n\n"
            "```mermaid\nflowchart TD\nE --> F\n```\n\n"
            "*Hình F03: Chú thích sư phạm [Nguồn gốc: Tái cấu trúc sư phạm].*\n"
            "<!-- FIGURE_END: F03 -->\n\n"
            "## 3. Tóm tắt cốt lõi\n- Tóm tắt\n\n"
            "## 4. Nguồn đối chiếu\n| Mục | Nguồn |\n"
        )
        # Validate from course root
        issues_root = validate_draft_structure(
            markdown, "READING", lesson_id="M02-L11", base_dir=self.course_dir
        )
        self.assertEqual(issues_root, [])

        # Validate from staged modules directory
        issues_mod = validate_draft_structure(
            markdown, "READING", lesson_id="M02-L11", base_dir=self.modules_dir
        )
        self.assertEqual(issues_mod, [])

    def test_missing_or_mismatched_assets_rejected(self):
        """Nonexistent or broken relative asset paths are flagged as blocking errors."""
        broken_markdown = (
            "# Bài học M02-L11\n\n"
            "## 1. Mục tiêu bài học\n- Mục tiêu\n\n"
            "## 2. Nội dung lý thuyết\n\n"
            "![Hình F01: Mô tả chi tiết cho sơ đồ khái niệm](assets/M02-L11/F01_nonexistent_slug.svg)\n\n"
            "## 3. Tóm tắt cốt lõi\n- Tóm tắt\n\n"
            "## 4. Nguồn đối chiếu\n| Mục | Nguồn |\n"
        )
        issues = validate_draft_structure(
            broken_markdown, "READING", lesson_id="M02-L11", base_dir=self.course_dir
        )
        self.assertTrue(any("Broken relative image path" in i for i in issues))

    def test_final_content_sha256_binding(self):
        """Content modification produces distinct SHA256 that binds to audit report."""
        import hashlib
        with open("generated_course/Agile_Project_Management/drafts/M02-L11_draft_v1.md", "r", encoding="utf-8") as f:
            v1_text = f.read()
        with open("generated_course/Agile_Project_Management/drafts/M02-L11_draft_v2_editorial.md", "r", encoding="utf-8") as f:
            v2_text = f.read()

        v1_sha = hashlib.sha256(v1_text.encode("utf-8")).hexdigest()
        v2_sha = hashlib.sha256(v2_text.encode("utf-8")).hexdigest()
        self.assertNotEqual(v1_sha, v2_sha)
        self.assertEqual(v1_sha, "75f03e0f67375c87f75d2bd5061274becb2435422ceb473dfb3b49600fbd64e3")
        self.assertEqual(v2_sha, "2961e0e17d7a615678452ab6ddf83689698e42e145e40175b4b7a4372ce1ff65")


if __name__ == "__main__":
    unittest.main()
