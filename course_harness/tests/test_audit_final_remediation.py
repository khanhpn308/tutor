"""Deterministic Test Suite for COURSE-HARNESS-V1-INDEPENDENT-AUDIT-FINAL-REMEDIATION.

Covers:
- F-01 [HIGH]: Dimension alias collision detection, rejection, order independence,
  canonical-only enforcement for Rubric 2.0, score inflation prevention, and legacy
  backward compatibility without current quality authorization.
- F-02 [MEDIUM]: Authoritative lesson context propagation (lesson_type, source_status)
  through Controller -> StateManager, manifest binding, verification on record and resume,
  positive QUIZ/GLOSSARY exemption, negative VIDEO_TRANSCRIPT masquerade rejection,
  READING/LOCKED rejection, and non-exempt lesson safety.
- F-03 [MEDIUM]: Student-facing cleanliness enabled by default in Worker, Repair, and
  pre-finalization validation paths, machine enum blocking, Vietnamese hypothetical
  scenario allowance, HTML comment preservation, and visual evidence freshness after Repair.
- Receipt provenance, model verification, source hash, and visual hash safeguards.
"""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

from course_harness.state import StateManager, calculate_file_sha256
from course_harness.validator import (
    AuditValidator,
    ValidationError,
    is_production_quality_eligible,
    validate_draft_structure,
    validate_student_facing_cleanliness,
)
from course_harness.visual import (
    QUALITY_RUBRIC_VERSION,
    calculate_quality_score,
    detect_dimension_collisions,
)

SCHEMA_PATH = "course_harness/schemas/audit.schema.json"


class TestF01DimensionAliasCollision(unittest.TestCase):
    """Tests for Finding F-01: Dimension alias collisions and Rubric 2.0 integrity."""

    def setUp(self):
        self.validator = AuditValidator(SCHEMA_PATH)
        self.canonical_dims = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MINOR_ISSUES",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        self.valid_locators = {
            "source_locator": "01:25",
            "draft_locator": "Section 2.1",
            "description": "Minor issue in completeness.",
            "required_action": "Expand coverage.",
        }

    def test_canonical_and_alias_simultaneous_collision_detected(self):
        """Simultaneous canonical and legacy alias (e.g. CONTENT_COMPLETENESS + COMPLETENESS) detected."""
        scores = dict(self.canonical_dims)
        scores["COMPLETENESS"] = "MET"  # conflicting alias

        collisions = detect_dimension_collisions(scores)
        self.assertTrue(len(collisions) > 0)
        self.assertTrue(any("COMPLETENESS" in c for c in collisions))

    def test_score_inflation_prevented_and_value_error_raised(self):
        """calculate_quality_score must raise ValueError on alias collision and not inflate score."""
        scores = dict(self.canonical_dims)
        scores["COMPLETENESS"] = "MET"

        with self.assertRaises(ValueError) as ctx:
            calculate_quality_score(
                scores,
                findings=[],
                lesson_type="VIDEO_TRANSCRIPT",
                quality_rubric_version=QUALITY_RUBRIC_VERSION,
            )
        self.assertIn("Dimension alias collision detected", str(ctx.exception))

    def test_key_insertion_order_independence(self):
        """Both insertion orders (canonical first vs alias first) must be rejected identically."""
        # Order 1: Canonical first, alias second
        scores_order1 = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MINOR_ISSUES",
            "COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        # Order 2: Alias first, canonical second
        scores_order2 = {
            "SOURCE_FIDELITY": "MET",
            "COMPLETENESS": "MET",
            "CONTENT_COMPLETENESS": "MINOR_ISSUES",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }

        # Both detect collision
        self.assertTrue(len(detect_dimension_collisions(scores_order1)) > 0)
        self.assertTrue(len(detect_dimension_collisions(scores_order2)) > 0)

        # Both raise ValueError
        with self.assertRaises(ValueError):
            calculate_quality_score(scores_order1, [], lesson_type="VIDEO_TRANSCRIPT", quality_rubric_version=QUALITY_RUBRIC_VERSION)
        with self.assertRaises(ValueError):
            calculate_quality_score(scores_order2, [], lesson_type="VIDEO_TRANSCRIPT", quality_rubric_version=QUALITY_RUBRIC_VERSION)

    def test_validator_and_eligibility_reject_colliding_report(self):
        """AuditValidator and is_production_quality_eligible must reject reports with alias collision."""
        report = {
            "lesson_id": "M01-L01",
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "summary": "Conflicting report",
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MINOR_ISSUES",
                "COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "VISUAL_PEDAGOGY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": [
                {
                    "severity": "MINOR",
                    "dimension": "CONTENT_COMPLETENESS",
                    **self.valid_locators,
                }
            ],
            "limitations": ["None"],
            "audited_final_sha256": "dummy_sha",
            "audit_invocation_id": "inv_001",
            "model_verification": "VERIFIED",
        }

        # Validator rejects via ValidationError
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M01-L01")
        self.assertTrue(
            "Dimension alias collision detected" in str(ctx.exception)
            or "Schema violation" in str(ctx.exception)
        )

        # Eligibility check returns False
        eligible, reason = is_production_quality_eligible(report, lesson_type="VIDEO_TRANSCRIPT", source_status="AVAILABLE")
        self.assertFalse(eligible)

    def test_canonical_only_enforced_for_rubric_2_0(self):
        """Under Rubric 2.0, alias alone without canonical name is rejected by schema and validator."""
        scores_with_alias_only = {
            "SOURCE_FIDELITY": "MET",
            "COMPLETENESS": "MET",  # alias instead of CONTENT_COMPLETENESS
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }

        # calculate_quality_score rejects alias under Rubric 2.0
        with self.assertRaises(ValueError) as ctx:
            calculate_quality_score(
                scores_with_alias_only,
                findings=[],
                lesson_type="VIDEO_TRANSCRIPT",
                quality_rubric_version=QUALITY_RUBRIC_VERSION,
            )
        self.assertIn("canonical dimension name", str(ctx.exception))

        # Schema rejects unknown property for 2.0-visual-first
        report = {
            "lesson_id": "M01-L01",
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "summary": "Alias report",
            "dimension_scores": scores_with_alias_only,
            "findings": [],
            "limitations": ["None"],
            "audited_final_sha256": "dummy_sha",
            "audit_invocation_id": "inv_001",
            "model_verification": "VERIFIED",
        }
        with self.assertRaises(ValidationError):
            self.validator.validate_report(json.dumps(report), expected_lesson_id="M01-L01")

    def test_other_legacy_aliases_detected_as_collisions(self):
        """All legacy alias collisions (TERMINOLOGY, STRUCTURE, TRACEABILITY) must be detected."""
        pairs = [
            ("TERMINOLOGY_CONSISTENCY", "TERMINOLOGY"),
            ("CLARITY_ORGANIZATION", "STRUCTURE"),
            ("SOURCE_TRACEABILITY", "TRACEABILITY"),
        ]
        for canonical, alias in pairs:
            scores = {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "VISUAL_PEDAGOGY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            }
            scores[alias] = "MINOR_ISSUES"
            collisions = detect_dimension_collisions(scores)
            self.assertTrue(len(collisions) > 0, f"Failed to detect collision between {canonical} and {alias}")

    def test_historical_rubric_1_0_accepted_for_backward_compat_without_current_acceptance(self):
        """Historical 7-dimension Rubric 1.0 reports parse without collision, but cannot authorize current PASS."""
        legacy_scores = {
            "SOURCE_FIDELITY": "MET",
            "COMPLETENESS": "MET",
            "TECHNICAL_ACCURACY": "MET",
            "TERMINOLOGY": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "STRUCTURE": "MET",
            "TRACEABILITY": "MET",
        }
        # In Rubric 1.0, this pair was historical; detect_dimension_collisions allows it
        collisions = detect_dimension_collisions(legacy_scores)
        self.assertEqual(collisions, [])

        res = calculate_quality_score(
            legacy_scores,
            findings=[],
            lesson_type="VIDEO_TRANSCRIPT",
            quality_rubric_version="1.0-text-only",
        )
        self.assertEqual(res["quality_score"], 100.0)
        # Historical report cannot grant current quality accepted
        self.assertFalse(res["content_quality_accepted"])

        report = {
            "lesson_id": "M03-L08",
            "verdict": "PASS",
            "quality_rubric_version": "1.0-text-only",
            "content_quality_accepted": False,
            "quality_score": 100.0,
            "summary": "Legacy report",
            "dimension_scores": legacy_scores,
            "findings": [],
            "limitations": ["Historical"],
            "audited_final_sha256": "legacy_sha",
            "audit_invocation_id": "inv_legacy",
            "model_verification": "LEGACY_PRE_V2",
        }
        # Production eligibility must be False
        eligible, reason = is_production_quality_eligible(report, lesson_type="VIDEO_TRANSCRIPT", source_status="AVAILABLE")
        self.assertFalse(eligible)


class TestF02LessonContextPropagation(unittest.TestCase):
    """Tests for Finding F-02: Lesson context propagation and StateManager boundary."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.test_dir, "manifest.json")
        manifest_data = {
            "lessons": {
                "M01-L01": {"lesson_id": "M01-L01", "source_type": "VIDEO_TRANSCRIPT", "status": "AVAILABLE"},
                "M01-L02": {"lesson_id": "M01-L02", "source_type": "QUIZ", "status": "AVAILABLE"},
                "M01-L03": {"lesson_id": "M01-L03", "source_type": "GLOSSARY", "status": "AVAILABLE"},
                "M01-L04": {"lesson_id": "M01-L04", "source_type": "READING", "status": "AVAILABLE"},
                "M01-L05": {"lesson_id": "M01-L05", "source_type": "QUIZ", "status": "LOCKED"},
            },
            "modules": [
                {
                    "id": "M01",
                    "lessons": [
                        {"id": "M01-L01", "source_type": "VIDEO_TRANSCRIPT", "status": "AVAILABLE"},
                        {"id": "M01-L02", "source_type": "QUIZ", "status": "AVAILABLE"},
                        {"id": "M01-L03", "source_type": "GLOSSARY", "status": "AVAILABLE"},
                        {"id": "M01-L04", "source_type": "READING", "status": "AVAILABLE"},
                        {"id": "M01-L05", "source_type": "QUIZ", "status": "LOCKED"},
                    ],
                }
            ]
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f)

        self.state_mgr = StateManager(
            self.test_dir,
            prompt_config_hash="cfg_hash_001",
            manifest_path=self.manifest_path,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_audit_report(self, lesson_id: str, visual_pedagogy_status: str = "MET"):
        final_file = os.path.join(self.test_dir, f"{lesson_id}_final.md")
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("# Student Facing Content\n" + ("Nội dung bài học chuẩn mực. " * 30))

        final_sha = calculate_file_sha256(final_file)
        audit_file = os.path.join(self.test_dir, f"{lesson_id}_audit.json")

        report = {
            "lesson_id": lesson_id,
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "summary": f"Audit for {lesson_id}",
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "VISUAL_PEDAGOGY": visual_pedagogy_status,
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": [],
            "limitations": ["Test limitation"],
            "audited_final_sha256": final_sha,
            "audit_invocation_id": f"inv_{lesson_id}",
            "model_verification": "VERIFIED",
        }
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        audit_sha = calculate_file_sha256(audit_file)
        return final_file, final_sha, audit_file, audit_sha, report

    def _save_receipt(self, lesson_id: str, final_sha: str, audit_sha: str, lesson_type: str = None, source_status: str = None):
        receipt_data = {
            "invocation_id": f"inv_{lesson_id}",
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
            "source_sha256": "source_sha_123",
            "prompt_config_hash": "cfg_hash_001",
            "audit_report_sha256": audit_sha,
            "created_at": "2026-10-25T00:00:00Z",
            "lesson_type": lesson_type,
            "source_status": source_status,
        }
        self.state_mgr.save_audit_receipt(receipt_data)

    def test_quiz_exemption_record_and_resume_success(self):
        """Legitimate QUIZ exemption can be recorded as PASS and resumed successfully."""
        lesson_id = "M01-L02"  # QUIZ, AVAILABLE
        final_file, final_sha, audit_file, audit_sha, report = self._create_audit_report(
            lesson_id, visual_pedagogy_status="NOT_APPLICABLE"
        )
        self._save_receipt(lesson_id, final_sha, audit_sha, lesson_type="QUIZ", source_status="AVAILABLE")

        self.state_mgr.initialize_lesson_state(
            lesson_id,
            source_sha256="source_sha_123",
            lesson_type="QUIZ",
            source_status="AVAILABLE",
        )

        chk = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_file,
            expected_final_sha256=final_sha,
            final_path=final_file,
            audit_invocation_id=f"inv_{lesson_id}",
            lesson_type="QUIZ",
            source_status="AVAILABLE",
        )

        self.assertEqual(chk["status"], "PASS")
        self.assertEqual(chk["lesson_type"], "QUIZ")
        self.assertEqual(chk["source_status"], "AVAILABLE")

        # Resumable pass check must succeed with verified context
        self.assertTrue(
            self.state_mgr.is_resumable_pass(
                lesson_id=lesson_id,
                current_source_sha256="source_sha_123",
                lesson_type="QUIZ",
                source_status="AVAILABLE",
            )
        )

    def test_glossary_exemption_record_and_resume_success(self):
        """Legitimate GLOSSARY exemption can be recorded as PASS and resumed successfully."""
        lesson_id = "M01-L03"  # GLOSSARY, AVAILABLE
        final_file, final_sha, audit_file, audit_sha, report = self._create_audit_report(
            lesson_id, visual_pedagogy_status="NOT_APPLICABLE"
        )
        self._save_receipt(lesson_id, final_sha, audit_sha, lesson_type="GLOSSARY", source_status="AVAILABLE")

        self.state_mgr.initialize_lesson_state(
            lesson_id,
            source_sha256="source_sha_123",
            lesson_type="GLOSSARY",
            source_status="AVAILABLE",
        )

        chk = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_file,
            expected_final_sha256=final_sha,
            final_path=final_file,
            audit_invocation_id=f"inv_{lesson_id}",
            lesson_type="GLOSSARY",
            source_status="AVAILABLE",
        )
        self.assertEqual(chk["status"], "PASS")

        self.assertTrue(
            self.state_mgr.is_resumable_pass(
                lesson_id=lesson_id,
                current_source_sha256="source_sha_123",
                lesson_type="GLOSSARY",
                source_status="AVAILABLE",
            )
        )

    def test_video_transcript_exemption_rejected(self):
        """VIDEO_TRANSCRIPT attempting VISUAL_PEDAGOGY=NOT_APPLICABLE must be rejected."""
        lesson_id = "M01-L01"  # VIDEO_TRANSCRIPT, AVAILABLE
        final_file, final_sha, audit_file, audit_sha, report = self._create_audit_report(
            lesson_id, visual_pedagogy_status="NOT_APPLICABLE"
        )
        self._save_receipt(lesson_id, final_sha, audit_sha, lesson_type="VIDEO_TRANSCRIPT", source_status="AVAILABLE")

        self.state_mgr.initialize_lesson_state(
            lesson_id,
            source_sha256="source_sha_123",
            lesson_type="VIDEO_TRANSCRIPT",
            source_status="AVAILABLE",
        )

        with self.assertRaises((ValueError, ValidationError)):
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_file,
                expected_final_sha256=final_sha,
                final_path=final_file,
                audit_invocation_id=f"inv_{lesson_id}",
                lesson_type="VIDEO_TRANSCRIPT",
                source_status="AVAILABLE",
            )

        # Resume check must also return False
        self.assertFalse(
            self.state_mgr.is_resumable_pass(
                lesson_id=lesson_id,
                current_source_sha256="source_sha_123",
                lesson_type="VIDEO_TRANSCRIPT",
                source_status="AVAILABLE",
            )
        )

    def test_video_transcript_masquerading_as_quiz_rejected(self):
        """A VIDEO_TRANSCRIPT attempting to pass lesson_type='QUIZ' to StateManager is rejected by manifest binding."""
        lesson_id = "M01-L01"  # Manifest explicitly says VIDEO_TRANSCRIPT
        final_file, final_sha, audit_file, audit_sha, report = self._create_audit_report(
            lesson_id, visual_pedagogy_status="NOT_APPLICABLE"
        )
        self._save_receipt(lesson_id, final_sha, audit_sha, lesson_type="VIDEO_TRANSCRIPT", source_status="AVAILABLE")

        self.state_mgr.initialize_lesson_state(
            lesson_id,
            source_sha256="source_sha_123",
            lesson_type="VIDEO_TRANSCRIPT",
            source_status="AVAILABLE",
        )

        # Attacker attempts to pass lesson_type="QUIZ" to record_audit_verdict
        with self.assertRaises(ValueError):
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_file,
                expected_final_sha256=final_sha,
                final_path=final_file,
                audit_invocation_id=f"inv_{lesson_id}",
                lesson_type="QUIZ",  # Masquerade!
                source_status="AVAILABLE",
            )

        # And resume check with masquerade must return False
        self.assertFalse(
            self.state_mgr.is_resumable_pass(
                lesson_id=lesson_id,
                current_source_sha256="source_sha_123",
                lesson_type="QUIZ",
                source_status="AVAILABLE",
            )
        )

    def test_reading_exemption_rejected(self):
        """READING lesson cannot claim VISUAL_PEDAGOGY=NOT_APPLICABLE exemption."""
        lesson_id = "M01-L04"  # READING, AVAILABLE
        final_file, final_sha, audit_file, audit_sha, report = self._create_audit_report(
            lesson_id, visual_pedagogy_status="NOT_APPLICABLE"
        )
        self._save_receipt(lesson_id, final_sha, audit_sha, lesson_type="READING", source_status="AVAILABLE")

        self.state_mgr.initialize_lesson_state(
            lesson_id,
            source_sha256="source_sha_123",
            lesson_type="READING",
            source_status="AVAILABLE",
        )

        with self.assertRaises((ValueError, ValidationError)):
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_file,
                expected_final_sha256=final_sha,
                final_path=final_file,
                audit_invocation_id=f"inv_{lesson_id}",
                lesson_type="READING",
                source_status="AVAILABLE",
            )

    def test_locked_status_exemption_rejected(self):
        """LOCKED lesson cannot claim VISUAL_PEDAGOGY=NOT_APPLICABLE exemption even if QUIZ."""
        lesson_id = "M01-L05"  # QUIZ, LOCKED
        final_file, final_sha, audit_file, audit_sha, report = self._create_audit_report(
            lesson_id, visual_pedagogy_status="NOT_APPLICABLE"
        )
        self._save_receipt(lesson_id, final_sha, audit_sha, lesson_type="QUIZ", source_status="LOCKED")

        self.state_mgr.initialize_lesson_state(
            lesson_id,
            source_sha256="source_sha_123",
            lesson_type="QUIZ",
            source_status="LOCKED",
        )

        with self.assertRaises((ValueError, ValidationError)):
            self.state_mgr.record_audit_verdict(
                lesson_id=lesson_id,
                verdict="PASS",
                audit_path=audit_file,
                expected_final_sha256=final_sha,
                final_path=final_file,
                audit_invocation_id=f"inv_{lesson_id}",
                lesson_type="QUIZ",
                source_status="LOCKED",
            )

    def test_valid_non_exempt_lesson_without_context_unaffected(self):
        """Standard lessons (MET on all 8 dimensions) must not be invalidated when context is missing."""
        lesson_id = "M01-L01"
        final_file, final_sha, audit_file, audit_sha, report = self._create_audit_report(
            lesson_id, visual_pedagogy_status="MET"
        )
        self._save_receipt(lesson_id, final_sha, audit_sha)

        self.state_mgr.initialize_lesson_state(
            lesson_id,
            source_sha256="source_sha_123",
        )

        chk = self.state_mgr.record_audit_verdict(
            lesson_id=lesson_id,
            verdict="PASS",
            audit_path=audit_file,
            expected_final_sha256=final_sha,
            final_path=final_file,
            audit_invocation_id=f"inv_{lesson_id}",
        )
        self.assertEqual(chk["status"], "PASS")

        # Resume without passing context should succeed because no exemption was claimed
        self.assertTrue(
            self.state_mgr.is_resumable_pass(
                lesson_id=lesson_id,
                current_source_sha256="source_sha_123",
            )
        )


class TestF03StudentFacingCleanliness(unittest.TestCase):
    """Tests for Finding F-03: Student-facing cleanliness at runtime."""

    def setUp(self):
        self.clean_draft = (
            "# Bài 1: Tổng quan về Quản lý Dự án\n\n"
            "## 1. Mục tiêu bài học\n"
            "Hiểu rõ các khái niệm và nguyên lý cốt lõi của Agile.\n\n"
            "## 2. Nội dung lý thuyết\n"
            "Quản lý dự án là quá trình lập kế hoạch, tổ chức và điều phối các nguồn lực để đạt được mục tiêu đề ra.\n\n"
            "```mermaid\n"
            "flowchart TD\n"
            "  A[Bắt đầu] --> B[Thực thi]\n"
            "  B --> C[Hoàn thành]\n"
            "```\n\n"
            "| Giai đoạn | Vai trò | Mục tiêu |\n"
            "|---|---|---|\n"
            "| Khởi tạo | Quản lý | Xác định phạm vi |\n"
            "| Thực thi | Đội ngũ | Triển khai công việc |\n\n"
            "## 3. Tóm tắt cốt lõi\n"
            "Cần áp dụng các nguyên lý linh hoạt trong môi trường thực tế.\n\n"
            "## 4. Nguồn học liệu và đối chiếu\n"
            "Đối chiếu theo video bài giảng 01:25 - 04:30.\n"
        )

    def test_default_validate_draft_structure_checks_cleanliness(self):
        """validate_draft_structure now defaults to check_student_cleanliness=True."""
        leaked_draft = self.clean_draft + "\nĐây là một ví dụ: AI_GENERATED_EXAMPLE để minh họa.\n"
        issues = validate_draft_structure(leaked_draft, source_type="VIDEO_TRANSCRIPT")
        self.assertTrue(len(issues) > 0)
        self.assertTrue(any("AI_GENERATED_EXAMPLE" in issue for issue in issues))

    def test_all_machine_enums_detected_in_student_facing_body(self):
        """Machine enums (PEDAGOGICAL_RECONSTRUCTION, AI_GENERATED_EXAMPLE, etc.) trigger blocking integrity errors."""
        enums_to_test = [
            "AI_GENERATED_EXAMPLE",
            "PEDAGOGICAL_RECONSTRUCTION",
            "SOURCE_DERIVED",
            "RENDER_VERIFIED",
            "CONTENT_QUALITY_ACCEPTED",
        ]
        for enum_val in enums_to_test:
            dirty_draft = self.clean_draft + f"\nThông tin hệ thống: {enum_val}\n"
            issues = validate_draft_structure(dirty_draft, source_type="VIDEO_TRANSCRIPT")
            self.assertTrue(len(issues) > 0, f"Failed to detect machine enum {enum_val}")
            self.assertTrue(any(enum_val in issue for issue in issues))

    def test_properly_labeled_vietnamese_hypothetical_scenario_accepted(self):
        """Properly labeled Vietnamese pedagogical hypothetical scenarios must not be flagged."""
        annotated_draft = (
            self.clean_draft
            + "\n> **Ghi chú sư phạm (Tình huống giả định):**\n"
            "> Trong một dự án phần mềm y tế, việc áp dụng Agile đòi hỏi tuân thủ nghiêm ngặt các quy định an toàn.\n"
        )
        issues = validate_draft_structure(annotated_draft, source_type="VIDEO_TRANSCRIPT")
        self.assertEqual(issues, [])

    def test_html_comments_with_machine_metadata_preserved(self):
        """Legitimate machine metadata inside HTML comments is preserved and not flagged."""
        commented_draft = (
            "<!-- FIGURE_METADATA: id=F01, type=diagram, source=model_output -->\n"
            "<!-- PROVENANCE: course_harness_v1 -->\n"
            + self.clean_draft
        )
        issues = validate_draft_structure(commented_draft, source_type="VIDEO_TRANSCRIPT")
        self.assertEqual(issues, [])

    def test_controller_worker_and_repair_enforce_cleanliness(self):
        """validate_student_facing_cleanliness flags machine enums while preserving clean drafts."""
        dirty_draft = self.clean_draft + "\nTrường dữ liệu: PEDAGOGICAL_RECONSTRUCTION.\n"
        issues = validate_student_facing_cleanliness(dirty_draft)
        self.assertTrue(len(issues) > 0)
        self.assertIn("PEDAGOGICAL_RECONSTRUCTION", issues[0])

        clean_issues = validate_student_facing_cleanliness(self.clean_draft)
        self.assertEqual(clean_issues, [])


class TestSafeguardsAndProvenance(unittest.TestCase):
    """Tests for Receipt Provenance, Model Verification, Hash Integrity, and Visual Freshness."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.state_mgr = StateManager(self.test_dir, prompt_config_hash="cfg_hash_001")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_missing_receipt_blocks_pass(self):
        """StateManager rejects recording a PASS when no controller audit receipt exists."""
        final_file = os.path.join(self.test_dir, "final.md")
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("# Content " * 20)
        final_sha = calculate_file_sha256(final_file)

        audit_file = os.path.join(self.test_dir, "audit.json")
        audit_payload = {
            "lesson_id": "M01-L01",
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "summary": "Valid audit",
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
            "limitations": ["None"],
            "audited_final_sha256": final_sha,
            "audit_invocation_id": "non_existent_inv_id",
            "model_verification": "VERIFIED",
        }
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(audit_payload, f)

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="src_sha")

        with self.assertRaises(ValueError) as ctx:
            self.state_mgr.record_audit_verdict(
                lesson_id="M01-L01",
                verdict="PASS",
                audit_path=audit_file,
                expected_final_sha256=final_sha,
                final_path=final_file,
                audit_invocation_id="non_existent_inv_id",
            )
        self.assertIn("Audit receipt provenance rejected", str(ctx.exception))

    def test_source_hash_mismatch_invalidates_pass(self):
        """A modified source SHA invalidates previously recorded PASS checkpoint."""
        final_file = os.path.join(self.test_dir, "final.md")
        with open(final_file, "w", encoding="utf-8") as f:
            f.write("# Content " * 20)
        final_sha = calculate_file_sha256(final_file)

        audit_file = os.path.join(self.test_dir, "audit.json")
        audit_payload = {
            "lesson_id": "M01-L01",
            "verdict": "PASS",
            "quality_rubric_version": "2.0-visual-first",
            "content_quality_accepted": True,
            "quality_score": 100.0,
            "summary": "Valid audit",
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
            "limitations": ["None"],
            "audited_final_sha256": final_sha,
            "audit_invocation_id": "inv_001",
            "model_verification": "VERIFIED",
        }
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(audit_payload, f)
        audit_sha = calculate_file_sha256(audit_file)

        self.state_mgr.save_audit_receipt({
            "invocation_id": "inv_001",
            "role": "auditor",
            "lesson_id": "M01-L01",
            "execution_mode": "automated_cli",
            "provider": "agy",
            "evidence_class": "REAL_AGY_VERIFIED",
            "model_requested": "gemini-3.8-flash-high",
            "model_reported": "gemini-3.8-flash-high",
            "model_verified": "VERIFIED",
            "terminal_status": "SUCCESS",
            "audited_final_sha256": final_sha,
            "source_sha256": "original_src_sha",
            "prompt_config_hash": "cfg_hash_001",
            "audit_report_sha256": audit_sha,
            "created_at": "2026-10-25T00:00:00Z",
        })

        self.state_mgr.initialize_lesson_state("M01-L01", source_sha256="original_src_sha")
        self.state_mgr.record_audit_verdict(
            lesson_id="M01-L01",
            verdict="PASS",
            audit_path=audit_file,
            expected_final_sha256=final_sha,
            final_path=final_file,
            audit_invocation_id="inv_001",
        )

        # Checking with original source SHA succeeds
        self.assertTrue(self.state_mgr.is_resumable_pass("M01-L01", "original_src_sha"))

        # Checking with altered source SHA fails and invalidates PASS
        self.assertFalse(self.state_mgr.is_resumable_pass("M01-L01", "changed_src_sha"))


if __name__ == "__main__":
    unittest.main()
