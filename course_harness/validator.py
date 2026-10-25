"""Deterministic Validator for Audit Reports and Draft Curriculum.

Validates:
1. Audit JSON against audit.schema.json
2. Verdict consistency (e.g. rejects PASS if HIGH/BLOCKING findings exist)
3. Mandatory finding fields (locators, required actions)
4. Draft structure and fidelity constraints
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import jsonschema

from course_harness.visual import (
    CURRENT_RUBRIC_VERSIONS,
    DEFINED_RUBRIC_2_0_DIMENSIONS,
    LEGACY_RUBRIC_VERSIONS,
    PERMITTED_VISUAL_EXEMPTION_LESSON_TYPES,
    QUALITY_RUBRIC_VERSION,
    TARGET_QUALITY_SCORE,
    calculate_quality_score,
    detect_dimension_collisions,
    extract_figures_from_markdown,
    is_safe_asset_path,
    normalize_dimension_name,
    validate_chart_fidelity,
    validate_figure_properties,
)

logger = logging.getLogger("course_harness.validator")

ALLOWED_VERDICTS = {"PASS", "FAIL", "INCONCLUSIVE"}
SEVERITIES_PREVENTING_PASS = {"HIGH", "BLOCKING"}


class ValidationError(ValueError):
    """Raised when an audit report or draft fails deterministic validation."""
    pass


def extract_json_payload(raw_text: str) -> Dict[str, Any]:
    """Extracts and parses JSON object from LLM response, stripping markdown fences if present."""
    text = raw_text.strip()
    
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block ```json ... ```
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
    if match:
        extracted = match.group(1).strip()
        try:
            return json.loads(extracted)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON within code fence: {e}") from e

    # Try finding outer braces { ... }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        snippet = text[first_brace : last_brace + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Failed to parse outer JSON braces: {e}") from e

    raise ValidationError("Could not find or parse valid JSON in model response")


class AuditValidator:
    """Deterministic validator for Independent Auditor JSON reports."""

    def __init__(self, schema_path: str):
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        self.validator = jsonschema.Draft7Validator(self.schema)

    def validate_report(
        self,
        raw_report: str,
        expected_lesson_id: str,
        lesson_type: Optional[str] = None,
        source_status: Optional[str] = None,
        strict_rubric_2_0: bool = False,
        final_markdown: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Validates the audit report JSON and enforces verdict consistency.
        
        Returns:
            Tuple of (parsed_json_dict, list_of_validation_warnings)
        """
        payload = extract_json_payload(raw_report)
        raw_cqa = payload.get("content_quality_accepted")
        errors = []
        warnings = []

        # 1. JSON Schema validation
        schema_errors = list(self.validator.iter_errors(payload))
        if schema_errors:
            for err in schema_errors:
                errors.append(f"Schema violation at '{err.json_path}': {err.message}")

        # 2. Check lesson_id match
        lesson_id = payload.get("lesson_id")
        if lesson_id != expected_lesson_id:
            errors.append(
                f"Lesson ID mismatch: expected '{expected_lesson_id}', report contains '{lesson_id}'"
            )

        # 3. Verdict validation
        verdict = payload.get("verdict")
        if verdict not in ALLOWED_VERDICTS:
            errors.append(f"Invalid verdict '{verdict}'. Allowed: {ALLOWED_VERDICTS}")

        # 4. Consistency check between verdict and findings
        findings = payload.get("findings", [])
        blocking_findings = [
            f for f in findings if f.get("severity") in SEVERITIES_PREVENTING_PASS
        ]

        if verdict == "PASS" and blocking_findings:
            errors.append(
                f"Verdict inconsistency: Verdict is 'PASS' but contains {len(blocking_findings)} "
                f"blocking finding(s) with severity HIGH/BLOCKING. Report must be FAIL."
            )

        # Check raw content_quality_accepted consistency with findings
        if raw_cqa is True and blocking_findings:
            errors.append(
                f"Consistency error: content_quality_accepted is True but report contains "
                f"{len(blocking_findings)} blocking finding(s) with severity HIGH/BLOCKING."
            )

        # Check visual_figures_audited against actual audited Markdown if provided
        if final_markdown is not None:
            from course_harness.visual import check_figure_markers, extract_figures_from_markdown
            marker_errs = check_figure_markers(final_markdown)
            for me in marker_errs:
                errors.append(f"VISUAL_MARKER_MALFORMED: {me}")
            actual_markdown_figs = extract_figures_from_markdown(final_markdown)
            untracked_figs = [
                f for f in actual_markdown_figs
                if f.get("is_untracked") or str(f.get("figure_id", "")).startswith("UNTRACKED")
            ]
            if untracked_figs:
                errors.append(
                    f"VISUAL_UNTRACKED_FIGURE: Untracked visual figure(s) detected in Markdown: {[f.get('figure_id') for f in untracked_figs]}"
                )
            audited_figs = payload.get("visual_figures_audited")
            if audited_figs is not None and audited_figs != len(actual_markdown_figs):
                errors.append(
                    f"Visual figures count mismatch: audit report declares visual_figures_audited={audited_figs}, "
                    f"but audited markdown contains {len(actual_markdown_figs)} figure(s)."
                )

        # 5. Check dimension_scores presence and completeness
        dimension_scores = payload.get("dimension_scores")
        if dimension_scores is not None and not isinstance(dimension_scores, dict):
            errors.append("Invalid dimension_scores format: must be an object/dict")
            dimension_scores = None

        if verdict == "PASS":
            if not dimension_scores:
                errors.append(
                    "Verdict inconsistency: Verdict is 'PASS' but report is missing required dimension_scores."
                )

        reported_version = payload.get("quality_rubric_version")
        if reported_version is not None:
            v_str = str(reported_version).strip()
            if (
                v_str != QUALITY_RUBRIC_VERSION
                and v_str not in LEGACY_RUBRIC_VERSIONS
                and not v_str.startswith("1.")
            ):
                errors.append(
                    f"Invalid or unknown quality_rubric_version: '{reported_version}'. "
                    f"Allowed: '{QUALITY_RUBRIC_VERSION}' or historical legacy versions."
                )

        # Rubric 2.0 explicit version requirements
        if reported_version == QUALITY_RUBRIC_VERSION and not dimension_scores:
            errors.append(
                f"Rubric 2.0 evaluation failed: missing required dimension_scores under '{QUALITY_RUBRIC_VERSION}'."
            )

        if dimension_scores:
            # Check for duplicate semantic dimensions and alias collisions
            collisions = detect_dimension_collisions(dimension_scores)
            if collisions:
                errors.append(
                    f"Dimension alias collision detected: {'; '.join(collisions)}. "
                    f"Conflicting canonical and alias dimensions are strictly prohibited."
                )

            # Strict canonical dimension check under Rubric 2.0
            if reported_version == QUALITY_RUBRIC_VERSION:
                non_canonical = [
                    dim for dim in dimension_scores.keys() if dim not in DEFINED_RUBRIC_2_0_DIMENSIONS
                ]
                if non_canonical:
                    errors.append(
                        f"Rubric 2.0 requires canonical dimension names only. "
                        f"Non-canonical dimension name(s) found: {sorted(non_canonical)}."
                    )

        if reported_version is None and dimension_scores:
            has_modern_dims = any(d in dimension_scores for d in ("VISUAL_PEDAGOGY", "FORMATTING"))
            all_8_present = DEFINED_RUBRIC_2_0_DIMENSIONS.issubset({normalize_dimension_name(d) for d in dimension_scores.keys()})
            if all_8_present or has_modern_dims:
                errors.append(
                    f"Modern rubric evaluation requires explicit quality_rubric_version: "
                    f"Expected '{QUALITY_RUBRIC_VERSION}'."
                )
            elif lesson_type in PERMITTED_VISUAL_EXEMPTION_LESSON_TYPES:
                errors.append(
                    f"Permitted visual exemption for lesson type '{lesson_type}' requires explicit "
                    f"quality_rubric_version == '{QUALITY_RUBRIC_VERSION}'."
                )

        if strict_rubric_2_0:
            if reported_version != QUALITY_RUBRIC_VERSION:
                errors.append(
                    f"Strict Rubric 2.0 required: reported version is '{reported_version}', expected '{QUALITY_RUBRIC_VERSION}'"
                )

        # 6. Authoritative calculation & Verdict Consistency
        if dimension_scores:
            failed_dimensions = [
                dim for dim, score in dimension_scores.items() if score == "FAILED"
            ]
            if verdict == "PASS" and failed_dimensions:
                errors.append(
                    f"Verdict inconsistency: Verdict is 'PASS' but dimension(s) {failed_dimensions} "
                    f"scored 'FAILED'. Report must be FAIL."
                )

            try:
                rubric_res = calculate_quality_score(
                    dimension_scores,
                    findings,
                    lesson_type=lesson_type,
                    quality_rubric_version=reported_version,
                    source_status=source_status,
                    auditor_verdict=verdict,
                )
            except ValueError as e:
                errors.append(f"Rubric calculation error: {e}")
                rubric_res = None

            if rubric_res is not None:
                recomputed_score = rubric_res["quality_score"]
                recomputed_version = rubric_res["quality_rubric_version"]
                recomputed_cqa = rubric_res["content_quality_accepted"]

                # Independent deterministic recomputation verification
                reported_score = payload.get("quality_score")
                if reported_score is not None:
                    try:
                        rep_score_val = float(reported_score)
                        if abs(rep_score_val - recomputed_score) > 0.5:
                            errors.append(
                                f"Quality score mismatch: reported score is {rep_score_val}, but recomputed "
                                f"score is {recomputed_score} (tolerance: 0.5)."
                            )
                    except (TypeError, ValueError):
                        errors.append(f"Invalid quality_score format in report: {reported_score}")

                payload["quality_score"] = recomputed_score
                payload["quality_rubric_version"] = recomputed_version
                payload["content_quality_accepted"] = recomputed_cqa

                # Single authoritative evaluation path: claimed acceptance cannot override failed gates
                if raw_cqa is True and not rubric_res["hard_gates_passed"]:
                    errors.append(
                        "Consistency error: content_quality_accepted was claimed as True in report, "
                        "but hard gates failed during authoritative recomputation."
                    )

                missing_dims = rubric_res.get("missing_dimensions", [])
                if verdict == "PASS" and missing_dims:
                    errors.append(
                        f"Verdict inconsistency: Verdict is 'PASS' but report is missing required "
                        f"dimension(s): {missing_dims}. Report must be FAIL."
                    )
                if verdict == "PASS" and recomputed_score < TARGET_QUALITY_SCORE:
                    errors.append(
                        f"Verdict inconsistency: Verdict is 'PASS' but quality score is {recomputed_score} "
                        f"(target threshold: {TARGET_QUALITY_SCORE}). Report must be FAIL."
                    )

                # Contradiction check: Auditor FAIL or INCONCLUSIVE claiming content_quality_accepted=True
                if verdict in ("FAIL", "INCONCLUSIVE") and raw_cqa is True:
                    errors.append(
                        f"Contradiction error: Report verdict is '{verdict}' but content_quality_accepted "
                        f"was claimed as True. FAIL or INCONCLUSIVE must never have content_quality_accepted=True."
                    )

                # Contradiction check: Auditor FAIL vs all dimensions MET and hard gates passed
                if verdict == "FAIL" and rubric_res["hard_gates_passed"]:
                    errors.append(
                        "Verdict contradiction: Report verdict is 'FAIL' but all dimensions are MET "
                        "with zero blocking findings. Conflicting quality decisions are rejected."
                    )
                # Contradiction check: Auditor PASS vs hard gates failed
                if verdict == "PASS" and not rubric_res["hard_gates_passed"]:
                    errors.append(
                        f"Verdict inconsistency: Verdict is 'PASS' but deterministic hard gates failed."
                    )

                # Rubric 2.0 integrity requirements
                if recomputed_version == QUALITY_RUBRIC_VERSION:
                    if missing_dims:
                        errors.append(
                            f"Rubric 2.0 evaluation failed: missing required dimension(s): {missing_dims}. "
                            f"All 8 rubric dimensions must be evaluated under '{QUALITY_RUBRIC_VERSION}'."
                        )
                    unauth_exemptions = rubric_res.get("unauthorized_exemptions", [])
                    if unauth_exemptions:
                        for u in unauth_exemptions:
                            errors.append(f"Rubric 2.0 exemption violation: {u}")
                else:
                    # Historical / legacy audit report: preserve version, cannot grant current acceptance
                    payload["content_quality_accepted"] = False
                    warnings.append(
                        f"Audit report is classified under historical rubric version '{recomputed_version}'; "
                        f"content_quality_accepted is False and cannot grant current quality acceptance under Rubric 2.0."
                    )
            else:
                payload["content_quality_accepted"] = False
        else:
            payload["content_quality_accepted"] = False

        if verdict in ("FAIL", "INCONCLUSIVE"):
            payload["content_quality_accepted"] = False

        if strict_rubric_2_0 and payload.get("content_quality_accepted") is not True:
            errors.append("Strict Rubric 2.0 validation failed: content_quality_accepted is not True")

        # 6. Locators validation
        for idx, finding in enumerate(findings):
            fid = finding.get("finding_id", f"idx-{idx}")
            s_loc = finding.get("source_locator", "").strip()
            d_loc = finding.get("draft_locator", "").strip()
            desc = finding.get("description", "").strip()
            req = finding.get("required_action", "").strip()

            if not s_loc:
                errors.append(f"Finding {fid} missing source_locator")
            if not d_loc:
                errors.append(f"Finding {fid} missing draft_locator")
            if not desc:
                errors.append(f"Finding {fid} missing description")
            if not req:
                errors.append(f"Finding {fid} missing required_action")

        if errors:
            raise ValidationError(
                f"Audit validation failed with {len(errors)} error(s):\n" + "\n".join(f"- {e}" for e in errors)
            )

        limitations = payload.get("limitations", [])
        if not limitations:
            warnings.append("Audit report includes no limitations notes.")

        return payload, warnings

    @staticmethod
    def is_production_quality_eligible(
        report: Dict[str, Any],
        lesson_type: Optional[str] = None,
        source_status: Optional[str] = None,
    ) -> Tuple[bool, str]:
        return is_production_quality_eligible(report, lesson_type, source_status)


def validate_draft_structure(
    draft_content: str,
    source_type: str,
    lesson_id: Optional[str] = None,
    raw_source_content: Optional[str] = None,
    require_visuals: bool = False,
    base_dir: Optional[str] = None,
    check_student_cleanliness: bool = True,
) -> List[str]:
    """Inspects draft content for structural integrity and pedagogical quality heuristics."""
    issues = []
    if not draft_content or len(draft_content.strip()) < 150:
        issues.append("Draft content is empty or too short (< 150 characters)")
        return issues

    # Check for title
    if not re.search(r'^#\s+.+', draft_content, re.MULTILINE):
        issues.append("Draft is missing top-level (#) title")

    # Check for essential sections based on source type
    if source_type in ("VIDEO_TRANSCRIPT", "READING"):
        has_objectives = bool(re.search(r'##\s+.*Mục tiêu|Learning Objectives', draft_content, re.IGNORECASE))
        has_theory = bool(re.search(r'##\s+.*(Nội dung|lý thuyết|Theory|kiến thức)', draft_content, re.IGNORECASE))
        has_summary = bool(re.search(r'##\s+.*(Tóm tắt|Key Takeaways|cốt lõi)', draft_content, re.IGNORECASE))
        has_traceability = bool(re.search(r'##\s+.*(Nguồn|Traceability|đối chiếu)', draft_content, re.IGNORECASE))

        if not has_objectives:
            issues.append("Missing Learning Objectives section")
        if not has_theory:
            issues.append("Missing Theory / Main Content section")
        if not has_summary:
            issues.append("Missing Summary / Key Takeaways section")
        if not has_traceability:
            issues.append("Missing Source Traceability section")

    elif source_type == "ACTIVITY":
        has_scenario = bool(re.search(r'bối cảnh|tình huống|scenario|nhiệm vụ|hướng dẫn', draft_content, re.IGNORECASE))
        if not has_scenario:
            issues.append("Activity draft missing scenario or task guidance section")

    # Check for fidelity hazards and distorted claims
    fidelity_violations = validate_source_fidelity_numerical_claims(draft_content, lesson_id=lesson_id)
    issues.extend(fidelity_violations)

    # Check that hypothetical examples do not attach false source timestamps
    hypo_violations = validate_labeled_hypothetical_examples(draft_content)
    issues.extend(hypo_violations)

    # Check student-facing metadata cleanliness if requested
    if check_student_cleanliness:
        cleanliness_issues = validate_student_facing_cleanliness(draft_content)
        issues.extend(cleanliness_issues)

    # Check visual pedagogy heuristics if visuals present or explicitly required
    visual_issues = validate_visual_pedagogy(
        draft_content=draft_content,
        source_type=source_type,
        lesson_id=lesson_id,
        raw_source_content=raw_source_content,
        require_visuals=require_visuals,
        base_dir=base_dir,
    )
    issues.extend(visual_issues)

    return issues


MACHINE_FACING_ENUMS = {
    "AI_GENERATED_EXAMPLE",
    "AI_GENERATED_ILLUSTRATION",
    "PEDAGOGICAL_RECONSTRUCTION",
    "SOURCE_DERIVED",
    "EXTERNAL_VERIFIED_ASSET",
    "RENDER_VERIFIED",
    "RENDER_NOT_VERIFIED",
    "RENDER_UNAVAILABLE",
    "RENDER_FAILED",
    "SPEC_VALID",
    "SPEC_INVALID",
    "VISUAL_REVIEWED",
    "VISUAL_LAYOUT_NOT_VERIFIED",
    "CONTENT_QUALITY_ACCEPTED",
    "HUMAN_ACCEPTED",
    "REAL_GEMINI_API_VERIFIED",
    "MOCK_SIMULATED",
}


def validate_student_facing_cleanliness(draft_content: str) -> List[str]:
    """Ensures draft does not expose machine-oriented pipeline metadata to students.
    
    Prohibits exposing in textbook body:
    - Internal provenance enum blocks: '> **Xuất xứ học liệu (Provenance):**'
    - Educational purpose metadata blocks: '> **Mục tiêu giáo dục:**'
    - Raw technical alt-text blocks: '> **Mô tả trực quan (Alt text):**'
    - Internal pipeline and provenance machine enums (e.g. AI_GENERATED_EXAMPLE).
    """
    violations = []
    # Strip HTML comments so internal comments are ignored
    content_no_comments = re.sub(r'<!--[\s\S]*?-->', '', draft_content)

    if re.search(r'>\s*\*\*(?:Xuất xứ học liệu|Provenance)\s*\(?Provenance\)?:\*\*', content_no_comments, re.IGNORECASE):
        violations.append("Student-facing markdown exposes internal pipeline metadata: 'Xuất xứ học liệu (Provenance)'")
    if re.search(r'>\s*\*\*(?:Mục tiêu giáo dục|Educational purpose):\*\*', content_no_comments, re.IGNORECASE):
        violations.append("Student-facing markdown exposes machine metadata: 'Mục tiêu giáo dục'")
    if re.search(r'>\s*\*\*(?:Mô tả trực quan|Alt text)\s*\(?Alt text\)?:\*\*', content_no_comments, re.IGNORECASE):
        violations.append("Student-facing markdown exposes verbose metadata block: 'Mô tả trực quan (Alt text)'")

    for enum_val in MACHINE_FACING_ENUMS:
        pattern = r'\b' + re.escape(enum_val) + r'\b'
        if re.search(pattern, content_no_comments):
            violations.append(f"Student-facing markdown exposes machine-facing enum: '{enum_val}'")

    return violations


def validate_visual_pedagogy(
    draft_content: str,
    source_type: str,
    lesson_id: Optional[str] = None,
    raw_source_content: Optional[str] = None,
    require_visuals: bool = False,
    base_dir: Optional[str] = None,
) -> List[str]:
    """Inspects draft content for visual learning design, figure specs, and chart fidelity."""
    issues = []
    figures = extract_figures_from_markdown(draft_content)

    # 1. Figure ID uniqueness and figure validation
    seen_ids = set()
    for fig in figures:
        fid = fig.get("figure_id", "")
        if fid in seen_ids:
            issues.append(f"Duplicate figure_id detected: '{fid}'")
        seen_ids.add(fid)

        prop_errors = validate_figure_properties(fig)
        issues.extend(prop_errors)

        if raw_source_content:
            chart_errors = validate_chart_fidelity(fig, raw_source_content)
            issues.extend(chart_errors)

    # 2. Visual density guideline check when required
    if require_visuals and source_type in ("VIDEO_TRANSCRIPT", "READING"):
        if len(figures) == 0:
            issues.append(
                f"Visual pedagogy issue: Substantive {source_type} lesson lacks explanatory visuals."
            )

    # 3. Path safety, asset check, and instructor image prohibition for image references
    prohibited_instructor_patterns = [
        r'\b(?:instructor|lecturer|presenter|author)[_-]?(?:photo|portrait|headshot|avatar|image)\b',
        r'\b(?:profile[_-]?photo|speaker[_-]?thumbnail|author[_-]?headshot)\b',
        r'\b(?:shraddha(?:[_-]?sahu)?)\b',
    ]

    img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', draft_content)
    # Also check HTML <img> tags
    for m in re.finditer(r'<img\s+[^>]*src=[\'"]([^\'"]+)[\'"][^>]*>', draft_content, re.IGNORECASE):
        tag_str = m.group(0)
        alt_m = re.search(r'alt=[\'"]([^\'"]*)[\'"]', tag_str, re.IGNORECASE)
        alt_val = alt_m.group(1) if alt_m else ""
        img_refs.append((alt_val, m.group(1)))

    for alt, path in img_refs:
        clean_path = path.strip()
        ref_text = f"{alt} {clean_path}".lower()
        for pat in prohibited_instructor_patterns:
            if re.search(pat, ref_text, re.IGNORECASE):
                issues.append(
                    f"PROHIBITED_INSTRUCTOR_IMAGE: Prohibited instructor/author photo or portrait reference detected: '{clean_path}' (alt: '{alt}')"
                )
                break

        if clean_path.startswith("http://") or clean_path.startswith("https://"):
            if "cloudfront.net" in clean_path or "coursera" in clean_path:
                issues.append(f"Prohibited external signed URL in image reference: '{clean_path}'")
        else:
            safe, reason = is_safe_asset_path(clean_path, base_dir=base_dir)
            if not safe:
                issues.append(f"Dangerous path traversal detected in image reference: '{clean_path}' ({reason})")

        # Check alternative text length
        if len(alt.strip()) < 10:
            issues.append(f"Image reference '{clean_path}' has missing or too brief alternative text (< 10 chars)")

        # Verify relative image existence if local path
        if not clean_path.startswith("http://") and not clean_path.startswith("https://") and not os.path.isabs(clean_path):
            candidates = []
            if base_dir:
                candidates.append(os.path.join(base_dir, clean_path))
            fixtures_base = os.path.join(os.path.dirname(__file__), "fixtures")
            candidates.append(os.path.join(fixtures_base, clean_path))
            candidates.append(os.path.join(os.getcwd(), clean_path))
            if not any(os.path.exists(c) for c in candidates):
                issues.append(f"Broken relative image path: '{clean_path}' does not exist on disk")

    return issues


GENERIC_FIDELITY_HAZARDS = [
    (
        r'đáp\s*án\s*chính\s*thức\s*là',
        "Ungrounded claim of official quiz answer ('đáp án chính thức là') detected without verification disclaimer.",
    ),
    (
        r'\[\s*\d{1,2}:\d{2}\s*ước\s*lượng\s*\]',
        "Estimated / fabricated timestamp detected ('ước lượng'). Only exact source timestamps are permitted.",
    ),
]

LESSON_SPECIFIC_FIDELITY_HAZARDS = {
    "M01-L07": [
        (
            r'3\s*ngày|15\s*phút',
            "Unsupported quantitative claim in M01-L07: '3 ngày' or '15 phút' email exchange does not appear in source transcript [01:51].",
        ),
        (
            r'6\s*tháng|200\s*trang|2\s*tuần',
            "Unsupported quantitative claim in M01-L07: '6 tháng', '200 trang', or '2 tuần' prototype does not appear in source transcript [03:42].",
        ),
        (
            r'17\s*(chuyên gia|người|tác giả|nhà sáng lập|thành viên)',
            "Unsupported historical claim in M01-L07: '17 chuyên gia' does not appear in source transcript [00:01].",
        ),
        (
            r'thành phẩm hoàn thiện|mọi sản phẩm bất kỳ',
            "Unsupported overstatement in M01-L07: 'thành phẩm hoàn thiện' or 'mọi sản phẩm bất kỳ' distorts the definition of 'Working software' [02:38].",
        ),
    ],
    "M03-L08": [
        (
            r'70%\s*(số\s*)?cây\s*bị\s*chết',
            "Distorted claim '70% cây bị chết' detected (raw source specifies 70% of customers had difficulty caring for plants, not 70% plant mortality).",
        ),
    ],
}


def validate_labeled_hypothetical_examples(content: str) -> List[str]:
    """Ensures hypothetical teaching examples are properly labeled and do not attach source timestamps.
    
    Rules:
    1. A section/block labeled as hypothetical must not attach source timestamps ([mm:ss])
       to invented details, which would falsely imply source authority.
    2. Properly labeled hypothetical examples are accepted without generic validation rejection.
    """
    violations = []
    # Find blocks marked as hypothetical examples
    pattern = re.compile(
        r'(?:>|#|\*)*\s*(?:Ghi chú sư phạm\s*)?\(?(?:Tình huống giả định|Ví dụ giả định|Tình huống mô phỏng|AI_GENERATED_EXAMPLE|AI_GENERATED_ILLUSTRATION)\)?[\s\S]*?(?=\n#{1,3}\s|\Z)',
        re.IGNORECASE,
    )
    for match in pattern.finditer(content):
        block = match.group(0)
        # Check if block falsely claims a source timestamp
        ts_match = re.findall(r'\[\s*\d{1,2}:\d{2}\s*\]', block)
        if ts_match:
            violations.append(
                f"Hypothetical teaching example must not attach source timestamp(s) {ts_match} to invented details."
            )
    return violations

FIDELITY_HAZARD_PATTERNS = GENERIC_FIDELITY_HAZARDS + [
    (
        r'70%\s*(số\s*)?cây\s*bị\s*chết',
        "Distorted claim '70% cây bị chết' detected (raw source specifies 70% of customers had difficulty caring for plants, not 70% plant mortality).",
    ),
]


def validate_source_fidelity_numerical_claims(
    content: str,
    custom_hazards: Optional[List[Tuple[str, str]]] = None,
    lesson_id: Optional[str] = None,
) -> List[str]:
    """Inspects text content for unsupported or distorted numerical/factual claims."""
    violations = []
    hazards = list(GENERIC_FIDELITY_HAZARDS)
    if lesson_id:
        if lesson_id in LESSON_SPECIFIC_FIDELITY_HAZARDS:
            hazards.extend(LESSON_SPECIFIC_FIDELITY_HAZARDS[lesson_id])
    else:
        # If lesson_id not provided, include all known patterns for general testing
        hazards = list(FIDELITY_HAZARD_PATTERNS)

    if custom_hazards:
        hazards.extend(custom_hazards)

    for pattern, message in hazards:
        if re.search(pattern, content, re.IGNORECASE):
            violations.append(message)

    return violations


def classify_draft_issues(issues: List[str]) -> Tuple[List[str], List[str]]:
    """Separates draft validation issues into blocking failures and nonblocking heuristic warnings.
    
    Nonblocking heuristic warnings:
    - Visual density guideline recommendations (e.g. substantive lesson lacks explanatory visuals).
    - Image reference brief alternative text warning (< 10 chars).
    
    Blocking failures:
    - Structural omissions (missing title, objectives, theory, summary, traceability).
    - Numerical and source fidelity violations / fabricated data / timestamp distortions.
    - Path traversal hazards and broken relative image assets.
    - Exposing student-facing pipeline metadata/enums.
    - Duplicate figure IDs or invalid figure specifications.
    """
    blocking = []
    warnings = []
    for issue in issues:
        if "Visual pedagogy issue: Substantive" in issue and "lacks explanatory visuals" in issue:
            warnings.append(issue)
        elif "missing or too brief alternative text (< 10 chars)" in issue:
            warnings.append(issue)
        else:
            blocking.append(issue)
    return blocking, warnings


def is_production_quality_eligible(
    report: Dict[str, Any],
    lesson_type: Optional[str] = None,
    source_status: Optional[str] = None,
) -> Tuple[bool, str]:
    """Central production quality eligibility check.
    
    Verifies:
    1. report.get("verdict") == "PASS"
    2. report.get("quality_rubric_version") == "2.0-visual-first"
    3. report.get("content_quality_accepted") is True
    4. Current quality hard gates passed authoritatively via calculate_quality_score:
       - No HIGH/BLOCKING findings
       - No FAILED dimensions
       - All 8 dimensions evaluated (or authorized exemption for nonvisual QUIZ/GLOSSARY)
       - No unauthorized exemptions
       - Calculated quality score >= 90.0
    """
    if not isinstance(report, dict):
        return False, "Report is not a dictionary"

    verdict = report.get("verdict")
    if verdict != "PASS":
        return False, f"Report verdict is '{verdict}', expected 'PASS'"

    rubric_version = report.get("quality_rubric_version")
    if rubric_version != QUALITY_RUBRIC_VERSION:
        return False, f"Rubric version is '{rubric_version}', expected '{QUALITY_RUBRIC_VERSION}'"

    if report.get("content_quality_accepted") is not True:
        return False, "content_quality_accepted is not True"

    dim_scores = report.get("dimension_scores")
    if not dim_scores or not isinstance(dim_scores, dict):
        return False, "Missing or invalid dimension_scores in report"

    findings = report.get("findings", [])
    if not isinstance(findings, list):
        return False, "Invalid findings format in report"

    # Duplicate semantic dimensions and alias collisions check
    collisions = detect_dimension_collisions(dim_scores)
    if collisions:
        return False, f"Dimension alias collision detected: {'; '.join(collisions)}"

    # Rubric 2.0 requires canonical dimension names only
    if rubric_version == QUALITY_RUBRIC_VERSION:
        non_canonical = [
            dim for dim in dim_scores.keys() if dim not in DEFINED_RUBRIC_2_0_DIMENSIONS
        ]
        if non_canonical:
            return False, f"Rubric 2.0 requires canonical dimension names only: {sorted(non_canonical)}"

    # Authoritative recomputation (never trust claimed score or status alone!)
    try:
        rubric_res = calculate_quality_score(
            dimension_scores=dim_scores,
            findings=findings,
            lesson_type=lesson_type,
            quality_rubric_version=rubric_version,
            source_status=source_status,
            auditor_verdict=verdict,
        )
    except ValueError as e:
        return False, f"Authoritative quality score computation failed: {e}"

    if not rubric_res.get("hard_gates_passed"):
        reasons = []
        if rubric_res.get("blocking_findings_count", 0) > 0:
            reasons.append(f"{rubric_res['blocking_findings_count']} blocking finding(s)")
        if rubric_res.get("failed_dimensions"):
            reasons.append(f"failed dimensions: {rubric_res['failed_dimensions']}")
        if rubric_res.get("missing_dimensions"):
            reasons.append(f"missing dimensions: {rubric_res['missing_dimensions']}")
        if rubric_res.get("unauthorized_exemptions"):
            reasons.append(f"unauthorized exemptions: {rubric_res['unauthorized_exemptions']}")
        if rubric_res.get("quality_score", 0.0) < TARGET_QUALITY_SCORE:
            reasons.append(f"score {rubric_res.get('quality_score')} < {TARGET_QUALITY_SCORE}")
        return False, f"Hard gates failed: {'; '.join(reasons)}"

    if rubric_res.get("content_quality_accepted") is not True:
        return False, "Authoritative content_quality_accepted recomputation returned False"

    # Reconcile visual manifest binding consistency if visual figures audited
    audited_figs = report.get("visual_figures_audited")
    vm_sha = report.get("visual_manifest_sha256")
    if audited_figs is not None and audited_figs > 0 and not vm_sha:
        return False, f"Audit report declares {audited_figs} visual figure(s) but lacks visual_manifest_sha256 binding"
    if vm_sha and audited_figs is not None and audited_figs == 0:
        return False, "Audit report declares visual_manifest_sha256 but visual_figures_audited is 0"

    return True, ""
