"""Tests for JSON Schema validation and verdict consistency."""

import json
import os
import unittest

from course_harness.validator import (
    AuditValidator,
    ValidationError,
    extract_json_payload,
    validate_draft_structure,
)


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.schema_path = "course_harness/schemas/audit.schema.json"
        self.validator = AuditValidator(self.schema_path)

    def test_extract_json_payload_direct(self):
        raw = '{"key": "value"}'
        self.assertEqual(extract_json_payload(raw), {"key": "value"})

    def test_extract_json_payload_fence(self):
        raw = 'Some thought here...\n```json\n{"lesson_id": "M01-L07"}\n```\nExtra text'
        self.assertEqual(extract_json_payload(raw), {"lesson_id": "M01-L07"})

    def test_valid_pass_report(self):
        report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "summary": "Everything is verified accurate.",
            "dimension_scores": {
                "SOURCE_FIDELITY": "MET",
                "COMPLETENESS": "MET",
                "TECHNICAL_ACCURACY": "MET",
                "TERMINOLOGY": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "STRUCTURE": "MET",
                "TRACEABILITY": "MET"
            },
            "findings": [
                {
                    "finding_id": "F-001",
                    "severity": "LOW",
                    "category": "TERMINOLOGY",
                    "source_locator": "01:51",
                    "draft_locator": "Mục 5",
                    "description": "Minor typo in glossary note.",
                    "required_action": "Correct spelling."
                }
            ],
            "limitations": ["Model shared family"]
        })
        payload, warnings = self.validator.validate_report(report, expected_lesson_id="M01-L07")
        self.assertEqual(payload["verdict"], "PASS")

    def test_inconsistent_pass_with_high_severity_rejected(self):
        """A report self-declaring PASS while having HIGH severity finding MUST be rejected."""
        report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "summary": "Invalid pass",
            "findings": [
                {
                    "finding_id": "F-001",
                    "severity": "HIGH",
                    "category": "SOURCE_FIDELITY",
                    "source_locator": "00:52",
                    "draft_locator": "Mục 3",
                    "description": "Fabricated an extra Agile value.",
                    "required_action": "Remove fabricated value."
                }
            ],
            "limitations": []
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(report, expected_lesson_id="M01-L07")
        self.assertIn("Verdict inconsistency", str(ctx.exception))

    def test_valid_fail_report(self):
        report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "FAIL",
            "summary": "Failed due to missing concepts.",
            "findings": [
                {
                    "finding_id": "F-001",
                    "severity": "HIGH",
                    "category": "COMPLETENESS",
                    "source_locator": "02:38",
                    "draft_locator": "Mục 3.2",
                    "description": "Omitted key discussion on team collaboration.",
                    "required_action": "Integrate 02:38 discussion into section 3.2."
                }
            ],
            "limitations": []
        })
        payload, _ = self.validator.validate_report(report, expected_lesson_id="M01-L07")
        self.assertEqual(payload["verdict"], "FAIL")

    def test_missing_finding_locator_rejected(self):
        report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "FAIL",
            "summary": "Incomplete finding",
            "findings": [
                {
                    "finding_id": "F-001",
                    "severity": "HIGH",
                    "category": "COMPLETENESS",
                    "source_locator": "",
                    "draft_locator": "Mục 3",
                    "description": "Something missing",
                    "required_action": "Fix it"
                }
            ],
            "limitations": []
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(report, expected_lesson_id="M01-L07")
        self.assertIn("missing source_locator", str(ctx.exception))

    def test_validate_draft_structure(self):
        good_draft = (
            "# Tiêu đề bài học\n\n"
            "## 1. Mục tiêu bài học (Learning Objectives)\n- Nắm vững kiến thức\n\n"
            "## 3. Nội dung lý thuyết trọng tâm (Theory)\n- Giải thích chi tiết...\n\n"
            "## 6. Tóm tắt cốt lõi (Key Takeaways)\n- Điểm 1\n\n"
            "## 8. Nguồn đối chiếu (Source Traceability)\n- Timestamp 01:51\n"
        )
        issues = validate_draft_structure(good_draft, "VIDEO_TRANSCRIPT")
        self.assertEqual(issues, [])

        bad_draft = "# Short\nHi."
        issues = validate_draft_structure(bad_draft, "VIDEO_TRANSCRIPT")
        self.assertTrue(len(issues) > 0)

    def test_inconsistent_pass_with_failed_dimension_rejected(self):
        """A report declaring PASS while having a FAILED dimension score MUST be rejected."""
        report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "summary": "Self-declared pass but fidelity failed",
            "dimension_scores": {
                "SOURCE_FIDELITY": "FAILED",
                "COMPLETENESS": "MET",
                "TECHNICAL_ACCURACY": "MET",
                "TERMINOLOGY": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "STRUCTURE": "MET",
                "TRACEABILITY": "MET"
            },
            "findings": [],
            "limitations": []
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(report, expected_lesson_id="M01-L07")
        self.assertIn("scored 'FAILED'", str(ctx.exception))
        self.assertIn("SOURCE_FIDELITY", str(ctx.exception))

    def test_numerical_claims_fidelity_negative_checks(self):
        """Negative test verifying detection of distorted numerical claims and ungrounded assertions."""
        hallucinated_draft = (
            "# Bài học thực hành\n\n"
            "## 1. Mục tiêu bài học (Learning Objectives)\n- Nắm vững kiến thức\n\n"
            "## 2. Bối cảnh dự án\n"
            "Dữ liệu cho thấy 70% cây bị chết trong tháng đầu tiên.\n\n"
            "## 3. Nội dung lý thuyết trọng tâm (Theory)\n"
            "Theo phân tích, đáp án chính thức là phương án B.\n"
            "Đoạn giảng tại [04:15 ước lượng] nêu rõ điều này.\n\n"
            "## 6. Tóm tắt cốt lõi (Key Takeaways)\n- Điểm 1\n\n"
            "## 8. Nguồn đối chiếu (Source Traceability)\n- Timestamp 01:51\n"
        )
        issues = validate_draft_structure(hallucinated_draft, "VIDEO_TRANSCRIPT")
        self.assertTrue(any("70% cây bị chết" in issue for issue in issues))
        self.assertTrue(any("đáp án chính thức là" in issue for issue in issues))
        self.assertTrue(any("ước lượng" in issue for issue in issues))

    def test_numerical_claims_fidelity_positive_controls(self):
        """Positive test verifying that valid source-grounded expressions are NOT flagged."""
        # 'dưới 4 tiêu chí' is semantically equivalent to 'three or fewer criteria' and must not be flagged
        valid_activity_draft = (
            "# Bài học thực hành M03-L08\n\n"
            "## 1. Mục tiêu bài học (Learning Objectives)\n- Nắm vững kiến thức\n\n"
            "## 2. Bối cảnh dự án\n"
            "Khảo sát sau đợt giao hàng cho thấy 70% khách hàng mới gặp khó khăn trong việc chăm sóc cây.\n\n"
            "## 3. Nội dung lý thuyết trọng tâm (Theory)\n"
            "Nếu một User Story đạt dưới 4 tiêu chí của I.N.V.E.S.T., hãy cân nhắc chỉnh sửa lại.\n"
            "Học viên có thể cân nhắc từ 3 tiêu chí trở xuống (*three or fewer criteria*).\n\n"
            "## 6. Tóm tắt cốt lõi (Key Takeaways)\n- Điểm 1\n\n"
            "## 8. Nguồn đối chiếu (Source Traceability)\n- Timestamp 01:51\n"
        )
        issues = validate_draft_structure(valid_activity_draft, "VIDEO_TRANSCRIPT")
        self.assertFalse(any("dưới 4 tiêu chí" in issue for issue in issues))
        self.assertFalse(any("70%" in issue for issue in issues))
        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
