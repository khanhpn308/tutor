"""Focused Regression Tests for Rubric Integrity Hotfix (F03-01, F03-02, F03-03).

Covers:
- F03-01: Rejection of missing VISUAL_PEDAGOGY and other mandatory dimensions under Rubric 2.0.
- F03-02: Strict allowlist restrictions on NOT_APPLICABLE by dimension and lesson type.
- F03-03: Preservation of legacy audit identity, historical versions, and preventing historical
          audits from granting current CONTENT_QUALITY_ACCEPTED.
- Single Authoritative Evaluation Path: Deterministic score recomputation, gate enforcement,
  and consistency checks.
"""

import json
import unittest

from course_harness.validator import (
    AuditValidator,
    ValidationError,
)
from course_harness.visual import (
    QUALITY_RUBRIC_VERSION,
    calculate_quality_score,
)


class TestRubricIntegrityHotfix(unittest.TestCase):
    """Test suite verifying fixes for F03-01, F03-02, and F03-03."""

    def setUp(self):
        self.validator = AuditValidator("course_harness/schemas/audit.schema.json")
        self.valid_locators = {
            "source_locator": "01:51",
            "draft_locator": "Section 3.1",
            "description": "Minor terminology issue.",
            "required_action": "Correct terminology.",
        }

    # =========================================================================
    # F03-01: Prevent Missing VISUAL_PEDAGOGY Bypass
    # =========================================================================

    def test_rubric_2_0_missing_visual_pedagogy_rejected_and_scores_85(self):
        """F03-01: Rubric 2.0 report missing VISUAL_PEDAGOGY fails validation, scores 85, no CQA."""
        scores_missing_visual = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }

        # 1. Direct score calculation under Rubric 2.0
        res = calculate_quality_score(
            scores_missing_visual,
            [],
            lesson_type="VIDEO_TRANSCRIPT",
            quality_rubric_version=QUALITY_RUBRIC_VERSION,
        )
        self.assertEqual(res["quality_score"], 85.0)
        self.assertFalse(res["hard_gates_passed"])
        self.assertFalse(res["content_quality_accepted"])
        self.assertEqual(res["verdict"], "FAIL")
        self.assertIn("VISUAL_PEDAGOGY", res["missing_dimensions"])

        # 2. Audit validator rejects report declaring 2.0-visual-first with missing VISUAL_PEDAGOGY
        report_json = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Report attempting to bypass visual pedagogy.",
            "dimension_scores": scores_missing_visual,
            "findings": [],
            "limitations": ["Test limitation."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(
                report_json,
                expected_lesson_id="M01-L07",
                lesson_type="VIDEO_TRANSCRIPT",
            )
        err_msg = str(ctx.exception)
        self.assertTrue(
            "VISUAL_PEDAGOGY" in err_msg or "missing required dimension" in err_msg.lower(),
            f"Expected error mentioning missing VISUAL_PEDAGOGY, got: {err_msg}",
        )

    def test_rubric_2_0_missing_other_mandatory_dimensions_rejected(self):
        """F03-01: Rubric 2.0 report missing SOURCE_FIDELITY or CONTENT_COMPLETENESS is rejected."""
        scores_missing_fidelity = {
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        res = calculate_quality_score(
            scores_missing_fidelity,
            [],
            quality_rubric_version=QUALITY_RUBRIC_VERSION,
        )
        self.assertEqual(res["quality_score"], 75.0)
        self.assertFalse(res["hard_gates_passed"])
        self.assertIn("SOURCE_FIDELITY", res["missing_dimensions"])

        report_json = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Report missing source fidelity.",
            "dimension_scores": scores_missing_fidelity,
            "findings": [],
            "limitations": ["Test limitation."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(report_json, expected_lesson_id="M01-L07")
        self.assertIn("SOURCE_FIDELITY", str(ctx.exception))

    # =========================================================================
    # F03-02: Restrict NOT_APPLICABLE
    # =========================================================================

    def test_arbitrary_not_applicable_source_fidelity_rejected(self):
        """F03-02: SOURCE_FIDELITY=NOT_APPLICABLE is strictly rejected and penalized."""
        scores = {
            "SOURCE_FIDELITY": "NOT_APPLICABLE",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        res = calculate_quality_score(
            scores,
            [],
            quality_rubric_version=QUALITY_RUBRIC_VERSION,
        )
        self.assertFalse(res["hard_gates_passed"])
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("SOURCE_FIDELITY" in e for e in res["unauthorized_exemptions"]))

        report_json = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Report skipping source fidelity.",
            "dimension_scores": scores,
            "findings": [],
            "limitations": ["Test limitation."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(report_json, expected_lesson_id="M01-L07")
        self.assertIn("SOURCE_FIDELITY", str(ctx.exception))

    def test_arbitrary_not_applicable_content_completeness_rejected(self):
        """F03-02: CONTENT_COMPLETENESS=NOT_APPLICABLE is strictly rejected."""
        scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "NOT_APPLICABLE",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "MET",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        report_json = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Report skipping completeness.",
            "dimension_scores": scores,
            "findings": [],
            "limitations": ["Test limitation."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(report_json, expected_lesson_id="M01-L07")
        self.assertIn("CONTENT_COMPLETENESS", str(ctx.exception))

    def test_video_transcript_with_unjustified_visual_pedagogy_not_applicable_rejected(self):
        """F03-02: Substantive VIDEO_TRANSCRIPT cannot mark VISUAL_PEDAGOGY=NOT_APPLICABLE."""
        scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        report_json = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Substantive lesson dodging visuals.",
            "dimension_scores": scores,
            "findings": [],
            "limitations": ["Test limitation."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(
                report_json,
                expected_lesson_id="M01-L07",
                lesson_type="VIDEO_TRANSCRIPT",
            )
        err_msg = str(ctx.exception)
        self.assertTrue(
            "VISUAL_PEDAGOGY" in err_msg and "VIDEO_TRANSCRIPT" in err_msg,
            f"Expected error noting VISUAL_PEDAGOGY disallowed on VIDEO_TRANSCRIPT, got: {err_msg}",
        )

    def test_reading_with_unjustified_visual_pedagogy_not_applicable_rejected(self):
        """F03-02: Substantive READING lesson cannot mark VISUAL_PEDAGOGY=NOT_APPLICABLE."""
        scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        report_json = json.dumps({
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Reading lesson dodging visuals.",
            "dimension_scores": scores,
            "findings": [],
            "limitations": ["Test limitation."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(
                report_json,
                expected_lesson_id="M02-L11",
                lesson_type="READING",
            )
        self.assertIn("READING", str(ctx.exception))

    def test_unknown_lesson_type_with_exemptions_rejected(self):
        """F03-02: Unknown lesson type with visual exemption fails closed."""
        scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        report_json = json.dumps({
            "lesson_id": "M01-L99",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Unknown lesson type exemption.",
            "dimension_scores": scores,
            "findings": [],
            "limitations": ["Test limitation."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(
                report_json,
                expected_lesson_id="M01-L99",
                lesson_type="CUSTOM_UNKNOWN_TYPE",
            )
        self.assertIn("CUSTOM_UNKNOWN_TYPE", str(ctx.exception))

    def test_locked_or_unavailable_source_blocks_visual_exemption(self):
        """F03-02: Locked or unavailable source cannot be awarded acceptance through exemptions."""
        scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        report_json = json.dumps({
            "lesson_id": "M01-L05",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Locked quiz trying to pass with exemption.",
            "dimension_scores": scores,
            "findings": [],
            "limitations": ["Source locked."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(
                report_json,
                expected_lesson_id="M01-L05",
                lesson_type="QUIZ",
                source_status="LOCKED",
            )
        self.assertIn("LOCKED", str(ctx.exception))

    def test_valid_quiz_with_permitted_visual_exemption_accepted(self):
        """F03-02 (Positive): Permitted QUIZ lesson with visual exemption normalizes to 100% PASS."""
        scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        report_json = json.dumps({
            "lesson_id": "M01-L08",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Legitimate quiz without diagrams.",
            "dimension_scores": scores,
            "findings": [],
            "limitations": ["Verified quiz."],
        })
        payload, warnings = self.validator.validate_report(
            report_json,
            expected_lesson_id="M01-L08",
            lesson_type="QUIZ",
            source_status="AVAILABLE",
        )
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["quality_score"], 100.0)
        self.assertTrue(payload["content_quality_accepted"])

    def test_valid_glossary_with_permitted_visual_exemption_accepted(self):
        """F03-02 (Positive): Permitted GLOSSARY entry with visual exemption normalizes to 100% PASS."""
        scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        report_json = json.dumps({
            "lesson_id": "M01-L10",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Glossary reference.",
            "dimension_scores": scores,
            "findings": [],
            "limitations": ["Glossary verified."],
        })
        payload, _ = self.validator.validate_report(
            report_json,
            expected_lesson_id="M01-L10",
            lesson_type="GLOSSARY",
            source_status="AVAILABLE",
        )
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["quality_score"], 100.0)
        self.assertTrue(payload["content_quality_accepted"])

    def test_valid_exemption_does_not_bypass_high_blocking_finding(self):
        """F03-02: Valid exemption does NOT bypass HIGH/BLOCKING findings."""
        scores = {
            "SOURCE_FIDELITY": "MET",
            "CONTENT_COMPLETENESS": "MET",
            "PEDAGOGICAL_QUALITY": "MET",
            "VISUAL_PEDAGOGY": "NOT_APPLICABLE",
            "TERMINOLOGY_CONSISTENCY": "MET",
            "SOURCE_TRACEABILITY": "MET",
            "CLARITY_ORGANIZATION": "MET",
            "FORMATTING": "MET",
        }
        report_json = json.dumps({
            "lesson_id": "M01-L08",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Quiz with high severity finding.",
            "dimension_scores": scores,
            "findings": [
                {
                    "finding_id": "F-001",
                    "severity": "HIGH",
                    "category": "SOURCE_FIDELITY",
                    "source_locator": "01:00",
                    "draft_locator": "Q1",
                    "description": "Fabricated official answer.",
                    "required_action": "Remove ungrounded answer.",
                }
            ],
            "limitations": ["Test limitation."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(
                report_json,
                expected_lesson_id="M01-L08",
                lesson_type="QUIZ",
            )
        self.assertIn("blocking finding", str(ctx.exception))

    # =========================================================================
    # F03-03: Preserve Legacy Audit Identity
    # =========================================================================

    def test_explicit_rubric_1_x_report_remains_historical(self):
        """F03-03: Explicit Rubric 1.x report retains historical version and cannot grant CQA."""
        legacy_report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": "1.0",
            "summary": "Historical v1.0 report.",
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
            "limitations": ["Historical audit."],
        })
        payload, warnings = self.validator.validate_report(legacy_report, "M01-L07")
        self.assertEqual(payload["quality_rubric_version"], "1.0")
        self.assertFalse(payload["content_quality_accepted"])
        self.assertEqual(payload["verdict"], "PASS")
        self.assertTrue(any("historical rubric version '1.0'" in w for w in warnings))

    def test_unknown_version_audit_classified_as_legacy_unknown(self):
        """F03-03: Audit report without rubric version metadata is classified as LEGACY_UNKNOWN."""
        report_no_ver = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "summary": "Report lacking version field.",
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
            "limitations": ["Legacy unversioned."],
        })
        payload, warnings = self.validator.validate_report(report_no_ver, "M01-L07")
        self.assertEqual(payload["quality_rubric_version"], "LEGACY_UNKNOWN")
        self.assertFalse(payload["content_quality_accepted"])
        self.assertTrue(any("LEGACY_UNKNOWN" in w for w in warnings))

    def test_historical_score_100_does_not_become_current_quality_acceptance(self):
        """F03-03: Historical 100/100 score does not grant content_quality_accepted=True."""
        legacy_report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_score": 100.0,
            "quality_rubric_version": "1.0-text-only",
            "summary": "Historical 100 score report.",
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
            "limitations": ["Historical."],
        })
        payload, _ = self.validator.validate_report(legacy_report, "M01-L07")
        self.assertEqual(payload["quality_score"], 100.0)
        self.assertEqual(payload["quality_rubric_version"], "1.0-text-only")
        self.assertFalse(payload["content_quality_accepted"])

    def test_unsupported_rubric_version_rejected(self):
        """F03-03: Unknown or invalid rubric versions are rejected."""
        bad_ver_report = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": "3.0-unsupported",
            "summary": "Invalid version report.",
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
            "limitations": ["Test."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(bad_ver_report, "M01-L07")
        self.assertIn("3.0-unsupported", str(ctx.exception))

    # =========================================================================
    # Single Authoritative Path & Recomputation Verification
    # =========================================================================

    def test_single_authoritative_path_recomputed_score_discrepancy_rejected(self):
        """Section 6: Discrepancy between reported and recomputed score is rejected."""
        # Reported score claims 100.0, but ratings recompute to lower
        report_json = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "FAIL",
            "quality_score": 100.0,  # False reported score
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Fabricated high score.",
            "dimension_scores": {
                "SOURCE_FIDELITY": "FAILED",  # Earns 0
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "VISUAL_PEDAGOGY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": [],
            "limitations": ["Test."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(report_json, "M01-L07")
        self.assertIn("Quality score mismatch", str(ctx.exception))

    def test_single_authoritative_path_claimed_cqa_true_cannot_override_failed_gates(self):
        """Section 6: Claimed content_quality_accepted=true cannot override failed gates."""
        report_json = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "FAIL",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "False claimed acceptance.",
            "content_quality_accepted": True,  # Cannot override FAILED dimension
            "dimension_scores": {
                "SOURCE_FIDELITY": "FAILED",
                "CONTENT_COMPLETENESS": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "VISUAL_PEDAGOGY": "MET",
                "TERMINOLOGY_CONSISTENCY": "MET",
                "SOURCE_TRACEABILITY": "MET",
                "CLARITY_ORGANIZATION": "MET",
                "FORMATTING": "MET",
            },
            "findings": [],
            "limitations": ["Test."],
        })
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate_report(report_json, "M01-L07")
        self.assertIn("Consistency error", str(ctx.exception))

    def test_current_rubric_pass_with_complete_evidence(self):
        """Current Rubric 2.0 with all 8 dimensions MET passes and receives CQA."""
        report_json = json.dumps({
            "lesson_id": "M01-L07",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "quality_score": 100.0,
            "content_quality_accepted": True,
            "summary": "Valid comprehensive report.",
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
            "limitations": ["Valid audit."],
        })
        payload, warnings = self.validator.validate_report(report_json, "M01-L07")
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["quality_score"], 100.0)
        self.assertTrue(payload["content_quality_accepted"])
        self.assertEqual(payload["quality_rubric_version"], QUALITY_RUBRIC_VERSION)

    def test_fully_evaluated_reading_accepted(self):
        """Fully evaluated READING lesson with all 8 dimensions MET passes."""
        report_json = json.dumps({
            "lesson_id": "M02-L11",
            "verdict": "PASS",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "summary": "Valid comprehensive reading lesson.",
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
            "limitations": ["Valid reading."],
        })
        payload, _ = self.validator.validate_report(
            report_json,
            expected_lesson_id="M02-L11",
            lesson_type="READING",
        )
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["quality_score"], 100.0)
        self.assertTrue(payload["content_quality_accepted"])


if __name__ == "__main__":
    unittest.main()
