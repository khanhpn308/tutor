"""Visual Learning Design and Pedagogical Diagram Pipeline for Course Harness v1.

Handles:
1. Visual plan and figure specification schemas.
2. Extraction of figures, Mermaid blocks, and metadata from draft lesson Markdown.
3. Deterministic validation of figure properties, relative paths, captions, alt text, and provenance.
4. Detection of fabricated quantitative data charts (fidelity guard).
5. Mermaid diagram asset export (.mmd) and local SVG rendering via mmdc (with honest fallback).
6. Quality Rubric calculation with VISUAL_PEDAGOGY dimension and NOT_APPLICABLE normalization.
"""

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import jsonschema

logger = logging.getLogger("course_harness.visual")

# Canonical visual types supported by Course Harness v1
SUPPORTED_VISUAL_TYPES = {
    "CONCEPT_MAP",
    "FLOWCHART",
    "SEQUENCE_DIAGRAM",
    "TIMELINE",
    "COMPARISON_DIAGRAM",
    "INFOGRAPHIC_SUMMARY",
    "DATA_CHART",
    "IMAGE_ASSET_REQUIRED",
}

# Core mandatory quality dimensions for curriculum evaluation
CORE_MANDATORY_DIMENSIONS: Set[str] = {
    "SOURCE_FIDELITY",
    "CONTENT_COMPLETENESS",
    "PEDAGOGICAL_QUALITY",
    "TERMINOLOGY_CONSISTENCY",
    "SOURCE_TRACEABILITY",
    "CLARITY_ORGANIZATION",
}

# Provenance classifications for visual learning aids
PROVENANCE_CLASSES = {
    "SOURCE_DERIVED",
    "PEDAGOGICAL_RECONSTRUCTION",
    "AI_GENERATED_ILLUSTRATION",
    "EXTERNAL_VERIFIED_ASSET",
}

# Rendering status states
RENDERING_STATUSES = {
    "RENDER_VERIFIED",
    "RENDER_NOT_VERIFIED",
    "RENDER_UNAVAILABLE",
    "RENDER_FAILED",
    "FALLBACK_MARKDOWN",
    "IMAGE_ASSET_REQUIRED",
}

# Visual acceptance stages (strictly separated, never conflated)
VISUAL_ACCEPTANCE_STAGES = {
    "SPEC_VALID",
    "RENDER_VERIFIED",
    "VISUAL_REVIEWED",
    "CONTENT_QUALITY_ACCEPTED",
}

# Visual layout review states
VISUAL_REVIEW_STATUSES = {
    "VISUAL_REVIEWED",
    "VISUAL_LAYOUT_NOT_VERIFIED",
}

# Quality Rubric version 2.0-visual-first
QUALITY_RUBRIC_VERSION = "2.0-visual-first"
TARGET_QUALITY_SCORE = 90.0

CURRENT_RUBRIC_VERSIONS: Set[str] = {QUALITY_RUBRIC_VERSION}
LEGACY_RUBRIC_VERSIONS: Set[str] = {"1.0", "1.0-text-only", "1.0-legacy", "LEGACY_UNKNOWN"}

# Authorized lesson types for VISUAL_PEDAGOGY exemption under Rubric 2.0
PERMITTED_VISUAL_EXEMPTION_LESSON_TYPES: Set[str] = {"QUIZ", "GLOSSARY", "SHORT_QUIZ"}

# Disallowed source statuses that block exemptions
BLOCKED_EXEMPTION_SOURCE_STATUSES: Set[str] = {"LOCKED", "UNAVAILABLE", "SOURCE_INCOMPLETE"}

# All 8 dimensions defined in Rubric 2.0
DEFINED_RUBRIC_2_0_DIMENSIONS: Set[str] = {
    "SOURCE_FIDELITY",
    "CONTENT_COMPLETENESS",
    "PEDAGOGICAL_QUALITY",
    "VISUAL_PEDAGOGY",
    "TERMINOLOGY_CONSISTENCY",
    "SOURCE_TRACEABILITY",
    "CLARITY_ORGANIZATION",
    "FORMATTING",
}

# Dimensions strictly prohibited from ever being NOT_APPLICABLE
STRICTLY_MANDATORY_DIMENSIONS: Set[str] = {
    "SOURCE_FIDELITY",
    "CONTENT_COMPLETENESS",
    "PEDAGOGICAL_QUALITY",
    "TERMINOLOGY_CONSISTENCY",
    "SOURCE_TRACEABILITY",
    "CLARITY_ORGANIZATION",
    "FORMATTING",
}

# 8 Weighted dimensions totaling 100 points
RUBRIC_WEIGHTS: Dict[str, float] = {
    "SOURCE_FIDELITY": 25.0,
    "CONTENT_COMPLETENESS": 15.0,
    "PEDAGOGICAL_QUALITY": 15.0,
    "VISUAL_PEDAGOGY": 15.0,
    "TERMINOLOGY_CONSISTENCY": 10.0,
    "SOURCE_TRACEABILITY": 10.0,
    "CLARITY_ORGANIZATION": 5.0,
    "FORMATTING": 5.0,
}

# Legacy weights totaling 100 points across the 6 historical core dimensions
LEGACY_RUBRIC_WEIGHTS: Dict[str, float] = {
    "SOURCE_FIDELITY": 25.0,
    "CONTENT_COMPLETENESS": 15.0,
    "PEDAGOGICAL_QUALITY": 15.0,
    "TERMINOLOGY_CONSISTENCY": 15.0,
    "SOURCE_TRACEABILITY": 15.0,
    "CLARITY_ORGANIZATION": 15.0,
}

# Dimension name normalization / aliases for backward compatibility
DIMENSION_ALIASES: Dict[str, str] = {
    "COMPLETENESS": "CONTENT_COMPLETENESS",
    "TECHNICAL_ACCURACY": "PEDAGOGICAL_QUALITY",
    "TERMINOLOGY": "TERMINOLOGY_CONSISTENCY",
    "STRUCTURE": "CLARITY_ORGANIZATION",
    "TRACEABILITY": "SOURCE_TRACEABILITY",
}

# Multipliers for grade levels
GRADE_MULTIPLIERS: Dict[str, float] = {
    "MET": 1.0,
    "MINOR_ISSUES": 0.7,
    "FAILED": 0.0,
}

VALID_MERMAID_TYPES: Set[str] = {
    "graph",
    "flowchart",
    "sequencediagram",
    "statediagram",
    "statediagram-v2",
    "classdiagram",
    "erdiagram",
    "timeline",
    "pie",
    "xychart-beta",
    "journey",
    "gitgraph",
    "c4context",
    "mindmap",
    "quadrantchart",
    "sankey-beta",
    "block-beta",
}


def slugify(text: str) -> str:
    """Converts a title or name to a safe alphanumeric slug."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9_-]+', '_', text)
    return text.strip('_')[:40] or "figure"


def calculate_sha256_bytes(data: bytes) -> str:
    """Calculates SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def calculate_sha256_str(text: str) -> str:
    """Calculates SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class VisualPlanValidator:
    """Validates Visual Plan payloads against visual_plan.schema.json."""

    def __init__(self, schema_path: Optional[str] = None):
        if schema_path is None:
            schema_path = os.path.join(
                os.path.dirname(__file__), "schemas", "visual_plan.schema.json"
            )
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Visual plan schema not found: {schema_path}")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        self.validator = jsonschema.Draft7Validator(self.schema)

    def validate_plan(self, plan_data: Dict[str, Any]) -> List[str]:
        """Returns list of schema violation messages."""
        errors = []
        for err in self.validator.iter_errors(plan_data):
            errors.append(f"VisualPlan schema violation at '{err.json_path}': {err.message}")
        return errors


def normalize_dimension_name(name: str) -> str:
    """Maps legacy dimension names to canonical rubric names."""
    canonical = DIMENSION_ALIASES.get(name, name)
    return canonical


def detect_dimension_collisions(dimension_scores: Dict[str, Any]) -> List[str]:
    """Detects duplicate semantic dimensions and conflicting canonical/alias combinations."""
    raw_keys = set(dimension_scores.keys())
    collisions = []

    for alias, canonical in DIMENSION_ALIASES.items():
        if alias in raw_keys and canonical in raw_keys:
            # In historical legacy 7-dimension reports, both TECHNICAL_ACCURACY and
            # PEDAGOGICAL_QUALITY exist simultaneously as distinct historical dimensions.
            # If no modern Rubric 2.0 dimensions are present, this historical pair is permitted.
            if alias == "TECHNICAL_ACCURACY" and canonical == "PEDAGOGICAL_QUALITY":
                has_modern_names = any(
                    k in raw_keys
                    for k in (
                        "CONTENT_COMPLETENESS",
                        "TERMINOLOGY_CONSISTENCY",
                        "CLARITY_ORGANIZATION",
                        "SOURCE_TRACEABILITY",
                        "VISUAL_PEDAGOGY",
                        "FORMATTING",
                    )
                )
                if not has_modern_names:
                    continue
            collisions.append(
                f"Conflicting canonical and alias dimensions detected: both '{canonical}' and alias '{alias}' are present."
            )

    return collisions


def calculate_quality_score(
    dimension_scores: Dict[str, str],
    findings: List[Dict[str, Any]],
    lesson_type: Optional[str] = None,
    quality_rubric_version: Optional[str] = None,
    source_status: Optional[str] = None,
    auditor_verdict: Optional[str] = None,
) -> Dict[str, Any]:
    """Calculates normalized quality score under Unified Quality Standard with strict rubric integrity.
    
    Hard gates:
    - Any finding with severity in ('HIGH', 'BLOCKING') prevents PASS.
    - Any dimension scored 'FAILED' prevents PASS.
    - Under Rubric 2.0, all 8 defined dimensions must be evaluated.
    - Missing mandatory dimensions prevent PASS.
    - Unauthorized NOT_APPLICABLE exemptions prevent PASS.
    - Quality score < 90.0 prevents PASS.
    - Auditor verdict in ('FAIL', 'INCONCLUSIVE') strictly prevents content_quality_accepted=True.
    
    Historical legacy reports retain their historical version identity and cannot grant
    current quality acceptance (content_quality_accepted=False).
    """
    # Detect duplicate semantic dimensions and alias collisions
    collisions = detect_dimension_collisions(dimension_scores)
    if collisions:
        raise ValueError(
            f"Dimension alias collision detected: {'; '.join(collisions)}. "
            f"Conflicting canonical and alias dimensions are strictly prohibited."
        )

    # 1. Determine effective rubric version and legacy classification
    version_str = str(quality_rubric_version).strip() if quality_rubric_version else None

    # For current Rubric 2.0, require canonical dimension names only
    if version_str == QUALITY_RUBRIC_VERSION:
        non_canonical = [
            dim for dim in dimension_scores.keys() if dim not in DEFINED_RUBRIC_2_0_DIMENSIONS
        ]
        if non_canonical:
            raise ValueError(
                f"Rubric 2.0 requires canonical dimension names only. "
                f"Non-canonical dimension name(s) found: {sorted(non_canonical)}."
            )

    normalized_scores: Dict[str, str] = {}
    for dim, score in dimension_scores.items():
        canonical = normalize_dimension_name(dim)
        if canonical in normalized_scores:
            if canonical == "PEDAGOGICAL_QUALITY" and dim == "TECHNICAL_ACCURACY":
                continue
            elif canonical == "PEDAGOGICAL_QUALITY" and "TECHNICAL_ACCURACY" in dimension_scores:
                normalized_scores[canonical] = score
                continue
        normalized_scores[canonical] = score

    if version_str:
        if version_str == QUALITY_RUBRIC_VERSION:
            effective_version = QUALITY_RUBRIC_VERSION
            is_legacy = False
            version_valid = True
        elif version_str in LEGACY_RUBRIC_VERSIONS or version_str.startswith("1."):
            effective_version = version_str
            is_legacy = True
            version_valid = True
        else:
            effective_version = version_str
            is_legacy = False
            version_valid = False
    else:
        # Version omitted:
        if "VISUAL_PEDAGOGY" in normalized_scores or "FORMATTING" in normalized_scores:
            # Evaluates the 8 modern dimensions, but classified as unversioned/legacy
            effective_version = "LEGACY_UNKNOWN"
            is_legacy = False
            version_valid = True
        else:
            # 7 or fewer dimensions without VISUAL_PEDAGOGY: classify as historical legacy
            effective_version = "LEGACY_UNKNOWN"
            is_legacy = True
            version_valid = True



    dimension_breakdown: Dict[str, Any] = {}
    missing_dimensions: List[str] = []
    unauthorized_exemptions: List[str] = []
    earned_weight = 0.0
    applicable_max_weight = 0.0

    if not version_valid:
        unauthorized_exemptions.append(
            f"Invalid or unknown quality_rubric_version: '{effective_version}'."
        )

    if is_legacy:
        # Legacy report evaluation: historical 7 dimensions
        # Legacy reports can NEVER grant current content_quality_accepted!
        target_weights = LEGACY_RUBRIC_WEIGHTS
        for dim, weight in target_weights.items():
            if dim not in normalized_scores:
                applicable_max_weight += weight
                dimension_breakdown[dim] = {
                    "weight": weight,
                    "score": "MISSING",
                    "earned": 0.0,
                    "applicable": True,
                }
                missing_dimensions.append(dim)
                continue

            score = normalized_scores[dim]
            applicable_max_weight += weight
            multiplier = GRADE_MULTIPLIERS.get(score, 0.0)
            dim_earned = weight * multiplier
            earned_weight += dim_earned

            dimension_breakdown[dim] = {
                "weight": weight,
                "score": score,
                "earned": dim_earned,
                "applicable": True,
            }

        if applicable_max_weight > 0:
            calculated_score = round((earned_weight / applicable_max_weight) * 100.0, 2)
        else:
            calculated_score = 0.0

        blocking_findings = [
            f for f in findings if f.get("severity") in ("HIGH", "BLOCKING")
        ]
        failed_dimensions = [
            dim for dim, data in dimension_breakdown.items() if data.get("score") == "FAILED"
        ]

        hard_gates_passed = (
            len(blocking_findings) == 0
            and len(failed_dimensions) == 0
            and len(missing_dimensions) == 0
            and calculated_score >= TARGET_QUALITY_SCORE
        )

        verdict = "PASS" if hard_gates_passed else "FAIL"

        return {
            "quality_rubric_version": effective_version,
            "quality_score": calculated_score,
            "quality_score_threshold": TARGET_QUALITY_SCORE,
            "hard_gates_passed": hard_gates_passed,
            "content_quality_accepted": False,  # Strict: Legacy reports CANNOT grant current quality acceptance!
            "verdict": verdict,
            "blocking_findings_count": len(blocking_findings),
            "failed_dimensions": failed_dimensions,
            "missing_dimensions": missing_dimensions,
            "unauthorized_exemptions": unauthorized_exemptions,
            "is_legacy": True,
            "applicable_weight_sum": applicable_max_weight,
            "dimension_breakdown": dimension_breakdown,
        }

    # Rubric 2.0 evaluation: all 8 dimensions defined in RUBRIC_WEIGHTS
    target_weights = RUBRIC_WEIGHTS
    for dim, weight in target_weights.items():
        if dim not in normalized_scores:
            if (
                dim == "VISUAL_PEDAGOGY"
                and effective_version != QUALITY_RUBRIC_VERSION
                and (str(lesson_type).upper() if lesson_type else "") in PERMITTED_VISUAL_EXEMPTION_LESSON_TYPES
                and (str(source_status).upper() if source_status else "") not in BLOCKED_EXEMPTION_SOURCE_STATUSES
            ):
                # Legacy / unversioned QUIZ/GLOSSARY exemption: VISUAL_PEDAGOGY was not applicable
                dimension_breakdown[dim] = {
                    "weight": weight,
                    "score": "NOT_APPLICABLE",
                    "earned": 0.0,
                    "applicable": False,
                }
                continue

            # Missing dimension under Rubric 2.0:
            # Never silently inject NOT_APPLICABLE!
            # Weight remains in denominator, earned is 0.0
            applicable_max_weight += weight
            dimension_breakdown[dim] = {
                "weight": weight,
                "score": "MISSING",
                "earned": 0.0,
                "applicable": True,
            }
            missing_dimensions.append(dim)
            continue

        score = normalized_scores[dim]

        if score == "NOT_APPLICABLE":
            # Check NOT_APPLICABLE eligibility
            if dim in STRICTLY_MANDATORY_DIMENSIONS and dim != "VISUAL_PEDAGOGY":
                unauthorized_exemptions.append(
                    f"Dimension '{dim}' cannot be NOT_APPLICABLE for evaluable lessons."
                )
                applicable_max_weight += weight
                dimension_breakdown[dim] = {
                    "weight": weight,
                    "score": "NOT_APPLICABLE (UNAUTHORIZED)",
                    "earned": 0.0,
                    "applicable": True,
                }
                continue

            if dim == "VISUAL_PEDAGOGY":
                norm_lesson_type = str(lesson_type).upper() if lesson_type else None
                norm_source_status = str(source_status).upper() if source_status else None

                if norm_source_status in BLOCKED_EXEMPTION_SOURCE_STATUSES:
                    unauthorized_exemptions.append(
                        f"VISUAL_PEDAGOGY exemption disallowed: source is {norm_source_status}. "
                        f"Locked or unavailable sources cannot receive quality acceptance through exemptions."
                    )
                    applicable_max_weight += weight
                    dimension_breakdown[dim] = {
                        "weight": weight,
                        "score": "NOT_APPLICABLE (UNAUTHORIZED_BLOCKED_SOURCE)",
                        "earned": 0.0,
                        "applicable": True,
                    }
                    continue

                if norm_lesson_type not in PERMITTED_VISUAL_EXEMPTION_LESSON_TYPES:
                    unauthorized_exemptions.append(
                        f"VISUAL_PEDAGOGY cannot be NOT_APPLICABLE for lesson type '{lesson_type}' "
                        f"(permitted only for {sorted(PERMITTED_VISUAL_EXEMPTION_LESSON_TYPES)} with available source)."
                    )
                    applicable_max_weight += weight
                    dimension_breakdown[dim] = {
                        "weight": weight,
                        "score": "NOT_APPLICABLE (UNAUTHORIZED_LESSON_TYPE)",
                        "earned": 0.0,
                        "applicable": True,
                    }
                    continue

                # Authorized exemption for QUIZ / GLOSSARY / SHORT_QUIZ
                dimension_breakdown[dim] = {
                    "weight": weight,
                    "score": "NOT_APPLICABLE",
                    "earned": 0.0,
                    "applicable": False,
                }
                continue

        applicable_max_weight += weight
        multiplier = GRADE_MULTIPLIERS.get(score, 0.0)
        dim_earned = weight * multiplier
        earned_weight += dim_earned

        dimension_breakdown[dim] = {
            "weight": weight,
            "score": score,
            "earned": dim_earned,
            "applicable": True,
        }

    if applicable_max_weight > 0:
        calculated_score = round((earned_weight / applicable_max_weight) * 100.0, 2)
    else:
        calculated_score = 0.0

    # Hard Gates evaluation
    blocking_findings = [
        f for f in findings if f.get("severity") in ("HIGH", "BLOCKING")
    ]
    failed_dimensions = [
        dim for dim, data in dimension_breakdown.items() if data.get("score") == "FAILED"
    ]

    hard_gates_passed = (
        version_valid
        and len(blocking_findings) == 0
        and len(failed_dimensions) == 0
        and len(missing_dimensions) == 0
        and len(unauthorized_exemptions) == 0
        and calculated_score >= TARGET_QUALITY_SCORE
    )

    verdict = "PASS" if hard_gates_passed else "FAIL"

    # Strict: Content quality accepted ONLY if hard gates passed, version is 2.0-visual-first,
    # and auditor verdict (if known) is PASS (FAIL or INCONCLUSIVE never accepted).
    content_quality_accepted = (
        hard_gates_passed
        and effective_version == QUALITY_RUBRIC_VERSION
        and (auditor_verdict is None or auditor_verdict == "PASS")
    )

    return {
        "quality_rubric_version": effective_version,
        "quality_score": calculated_score,
        "quality_score_threshold": TARGET_QUALITY_SCORE,
        "hard_gates_passed": hard_gates_passed,
        "content_quality_accepted": content_quality_accepted,
        "verdict": verdict,
        "blocking_findings_count": len(blocking_findings),
        "failed_dimensions": failed_dimensions,
        "missing_dimensions": missing_dimensions,
        "unauthorized_exemptions": unauthorized_exemptions,
        "is_legacy": False,
        "applicable_weight_sum": applicable_max_weight,
        "dimension_breakdown": dimension_breakdown,
    }


def check_figure_markers(content: str) -> List[str]:
    """Validates pairing, nesting, and structural integrity of FIGURE_START / FIGURE_END markers.
    
    Returns a list of error descriptions (empty list if all markers are valid).
    """
    errors: List[str] = []

    # 1. First, search for any malformed or incomplete FIGURE_START / FIGURE_END occurrences
    valid_marker_pattern = re.compile(
        r'<!--\s*FIGURE_(START|END):\s*([a-zA-Z0-9_-]+)\s*-->',
        re.IGNORECASE,
    )

    valid_spans: List[Tuple[int, int]] = []
    ordered_markers: List[Tuple[int, str, str]] = []
    for m in valid_marker_pattern.finditer(content):
        valid_spans.append((m.start(), m.end()))
        ordered_markers.append((m.start(), m.group(1).upper(), m.group(2).strip()))

    # Any occurrence of FIGURE_START or FIGURE_END not inside a valid span is malformed/incomplete
    suspicious_pattern = re.compile(r'FIGURE_(?:START|END)', re.IGNORECASE)
    for sm in suspicious_pattern.finditer(content):
        s_pos = sm.start()
        is_inside_valid = any(v_start <= s_pos < v_end for v_start, v_end in valid_spans)
        if not is_inside_valid:
            line_start = content.rfind("\n", 0, s_pos)
            line_start = 0 if line_start == -1 else line_start + 1
            line_end = content.find("\n", s_pos)
            line_end = len(content) if line_end == -1 else line_end
            raw_line = content[line_start:line_end].strip()
            errors.append(f"Malformed or incomplete figure marker: '{raw_line}'")

    # 2. Check pairing, nesting, and matching IDs using a stack
    stack: List[Tuple[str, int]] = []

    for start_pos, marker_type, fig_id in ordered_markers:
        if marker_type == "START":
            if stack:
                open_id, _ = stack[-1]
                errors.append(
                    f"Nested FIGURE_START detected: '{fig_id}' declared inside unclosed '{open_id}'"
                )
            stack.append((fig_id, start_pos))
        elif marker_type == "END":
            if not stack:
                errors.append(
                    f"Orphaned FIGURE_END detected: '{fig_id}' without preceding FIGURE_START"
                )
            else:
                open_id, _ = stack.pop()
                if open_id != fig_id:
                    errors.append(
                        f"Mismatched figure marker: FIGURE_START '{open_id}' closed by FIGURE_END '{fig_id}'"
                    )

    if stack:
        for unclosed_id, _ in stack:
            errors.append(f"Unclosed FIGURE_START detected: '{unclosed_id}' has no matching FIGURE_END")

    return errors


def extract_figures_from_markdown(content: str) -> List[Dict[str, Any]]:
    """Extracts figure specifications, Mermaid code, captions, and metadata from lesson markdown.
    
    Supports:
    1. Explicit figure blocks:
       <!-- FIGURE_START: F01 --> ... <!-- FIGURE_END: F01 -->
    2. Structured Visual Plan blocks:
       ```json:visual_plan ... ``` or ```visual_plan ... ```
    3. Standalone and mixed Mermaid blocks with deterministic figure IDs or metadata.
       Unregistered or ambiguous Mermaid blocks are flagged with is_untracked=True.
    """
    figures: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()

    # Enumerate all Mermaid blocks in markdown with character spans
    mermaid_pattern = re.compile(r'```mermaid\s*\n?([\s\S]*?)```', re.MULTILINE)
    all_mermaids: List[Dict[str, Any]] = []
    for m in mermaid_pattern.finditer(content):
        all_mermaids.append({
            "start": m.start(),
            "end": m.end(),
            "raw_code": m.group(1).strip(),
            "clean_code": re.sub(r'<!--[\s\S]*?-->', '', m.group(1)).strip(),
        })

    claimed_mermaid_spans: Set[int] = set()

    # Pattern 1: Explicit FIGURE_START blocks
    pattern_explicit = re.compile(
        r'<!--\s*FIGURE_START:\s*([a-zA-Z0-9_-]+)\s*-->([\s\S]*?)<!--\s*FIGURE_END:\s*\1\s*-->',
        re.MULTILINE,
    )
    for match in pattern_explicit.finditer(content):
        fig_id = match.group(1).strip()
        body = match.group(2)
        start_pos = match.start()
        end_pos = match.end()

        # Claim all enclosed mermaid blocks to avoid double counting
        for idx, m in enumerate(all_mermaids):
            if start_pos <= m["start"] and m["end"] <= end_pos:
                claimed_mermaid_spans.add(idx)

        fig_dict = _parse_figure_block(fig_id, body)
        if fig_dict:
            fig_dict["_span"] = (start_pos, end_pos)
            fig_dict["is_untracked"] = False
            figures.append(fig_dict)
            seen_ids.add(fig_id)

    # Pattern 2: Embedded JSON Visual Plan blocks
    pattern_json_plan = re.compile(
        r'```(?:json:)?visual_plan\s*([\s\S]*?)\s*```',
        re.IGNORECASE,
    )
    for match in pattern_json_plan.finditer(content):
        start_pos = match.start()
        end_pos = match.end()
        for idx, m in enumerate(all_mermaids):
            if start_pos <= m["start"] and m["end"] <= end_pos:
                claimed_mermaid_spans.add(idx)
        try:
            plan_obj = json.loads(match.group(1).strip())
            plan_figs = plan_obj.get("figures", [])
            for pf in plan_figs:
                pid = pf.get("figure_id")
                if pid:
                    pf["_span"] = (start_pos, end_pos)
                    pf["is_untracked"] = False
                    figures.append(pf)
                    seen_ids.add(pid)
        except Exception as e:
            logger.warning(f"Failed to parse visual_plan json block: {e}")

    # Pattern 3: Standalone / Unclaimed Mermaid blocks (including mixed documents)
    has_explicit = len(figures) > 0
    for idx, m in enumerate(all_mermaids):
        if idx in claimed_mermaid_spans:
            continue

        raw_mermaid = m["raw_code"]
        clean_mermaid = m["clean_code"]

        # Check for deterministic figure ID in comments, headers, or captions
        pre_text = content[max(0, m["start"] - 400): m["start"]]
        post_text = content[m["end"]: min(len(content), m["end"] + 600)]

        # 1. Comment inside Mermaid
        c_inside = re.search(
            r'<!--\s*(?:figure:\s*(?:[^>]*?\s+)?id=[\"\']?|FIGURE_START:\s*)([a-zA-Z0-9_-]+)',
            raw_mermaid,
            re.IGNORECASE,
        ) or re.search(r'%%\s*figure:\s*id=[\"\']?([a-zA-Z0-9_-]+)', raw_mermaid, re.IGNORECASE)

        # 2. Comment immediately before
        c_before = re.search(
            r'<!--\s*(?:figure:\s*(?:[^>]*?\s+)?id=[\"\']?|FIGURE_START:\s*)([a-zA-Z0-9_-]+)[^>]*-->\s*$',
            pre_text,
            re.IGNORECASE,
        )

        # 3. Header immediately before
        h_before = re.search(
            r'#+\s*(?:Hình|Figure|Sơ đồ)\s*([a-zA-Z0-9_-]+)[:\.\s-]+([^\n]+)\s*$',
            pre_text,
            re.IGNORECASE,
        )

        # 4. Caption immediately after
        first_section = re.split(r'\n(?=```|#)', post_text)[0]
        cap_after = re.search(
            r'[\*_](?:Hình|Figure|Sơ đồ)\s*([a-zA-Z0-9_-]+)[:\.\s-]+([^\*_\n]+)[\*_]',
            first_section,
            re.IGNORECASE,
        )

        det_id = None
        if c_before:
            det_id = c_before.group(1).strip()
        elif c_inside:
            det_id = c_inside.group(1).strip()
        elif cap_after:
            det_id = cap_after.group(1).strip()
        elif h_before:
            det_id = h_before.group(1).strip()

        is_untracked = False
        if det_id:
            if det_id.isdigit():
                fig_id = f"F{int(det_id):02d}"
            else:
                fig_id = det_id
        else:
            # Check if this is a pure standalone document with standard pedagogical metadata
            has_pedagogical_meta = bool(
                re.search(r'>\s*\*\*(?:Chú thích|Mô tả trực quan|Mục tiêu giáo dục|Xuất xứ học liệu)', post_text)
            )
            if not has_explicit and has_pedagogical_meta and len(all_mermaids) == 1:
                fig_id = f"F{len(figures)+1:02d}"
                is_untracked = False
            else:
                # In mixed document or lacking deterministic ID/metadata: mark as untracked
                fig_id = f"UNTRACKED_F{len(figures)+1:02d}"
                is_untracked = True

        # Extract title
        title = ""
        if h_before:
            title = h_before.group(2).strip()
        elif cap_after:
            title = cap_after.group(2).strip()
        else:
            chuthich_match = re.search(r'>\s*\*\*(?:Chú thích|Title|Tiêu đề):\*\*\s*([^\n]+)', post_text)
            title = chuthich_match.group(1).strip() if chuthich_match else f"Sơ đồ minh họa {fig_id}"

        # Extract caption
        if cap_after:
            caption = f"Hình {fig_id}: {cap_after.group(2).strip()}"
        else:
            chuthich_match = re.search(r'>\s*\*\*(?:Chú thích|Caption):\*\*\s*([^\n]+)', post_text)
            caption = f"Hình {fig_id}: {chuthich_match.group(1).strip()}" if chuthich_match else f"Hình {fig_id}: {title}"

        # Extract alt_text
        alt_match = re.search(
            r'>\s*\*\*(?:Mô tả trực quan|Mô tả|Alt text)\s*\(?Alt text\)?:\*\*\s*([^\n]+)',
            post_text,
            re.IGNORECASE,
        )
        alt_text = alt_match.group(1).strip() if alt_match else (caption or f"Sơ đồ học tập mã {fig_id}")

        # Extract educational purpose
        purpose_match = re.search(
            r'>\s*\*\*(?:Mục tiêu giáo dục|Mục đích|Educational purpose):\*\*\s*([^\n]+)',
            post_text,
            re.IGNORECASE,
        )
        educational_purpose = purpose_match.group(1).strip() if purpose_match else f"Minh họa trực quan kiến thức cho {fig_id}"

        # Extract related learning objective
        obj_match = re.search(
            r'>\s*\*\*(?:Mục tiêu bài học liên quan|Learning objective):\*\*\s*([^\n]+)',
            post_text,
            re.IGNORECASE,
        )
        related_objective = obj_match.group(1).strip() if obj_match else "Hỗ trợ làm rõ nội dung trọng tâm bài học"

        # Extract provenance class
        prov_match = re.search(
            r'>\s*\*\*(?:Xuất xứ học liệu|Nguồn & Xuất xứ|Provenance)\s*\(?Provenance\)?:\*\*\s*(?:`|\[)?([A-Z_]+)(?:`|\])?',
            post_text,
            re.IGNORECASE,
        )
        provenance_class = "PEDAGOGICAL_RECONSTRUCTION"
        if prov_match and prov_match.group(1).strip().upper() in PROVENANCE_CLASSES:
            provenance_class = prov_match.group(1).strip().upper()

        # Extract source locators
        loc_match = re.findall(r'\[\s*(\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?)\s*\]', post_text[:300])
        valid_locators = []
        for loc in loc_match:
            parts = re.split(r'[-\s–]+', loc)
            for p in parts:
                p_clean = p.strip()
                if re.match(r'^\d{1,2}:\d{2}$', p_clean) and p_clean not in valid_locators:
                    valid_locators.append(p_clean)
        source_locators = valid_locators if valid_locators else ["00:01"]

        fig_type = _infer_visual_type_from_mermaid(clean_mermaid)
        figures.append({
            "figure_id": fig_id,
            "title": title,
            "visual_type": fig_type,
            "educational_purpose": educational_purpose,
            "related_learning_objective": related_objective,
            "source_locators": source_locators,
            "provenance_class": provenance_class,
            "alt_text": alt_text,
            "caption": caption,
            "mermaid_code": clean_mermaid,
            "rendering_status": "RENDER_NOT_VERIFIED",
            "is_untracked": is_untracked,
            "_span": (m["start"], m["end"]),
        })
        seen_ids.add(fig_id)

    # Sort figures by character start position in content
    figures.sort(key=lambda f: f.get("_span", (0, 0))[0])
    for f in figures:
        f.pop("_span", None)

    return figures


def _parse_figure_block(fig_id: str, body: str) -> Dict[str, Any]:
    """Helper to parse figure properties from within a FIGURE_START block."""
    # Extract Title from #### or ### header
    title_match = re.search(r'#+\s*(?:Hình\s*[a-zA-Z0-9_-]+[:\.\s-]+)?([^\n]+)', body)
    title = title_match.group(1).strip() if title_match else f"Sơ đồ {fig_id}"

    # Extract Mermaid code
    mmd_match = re.search(r'```mermaid\s*([\s\S]*?)\s*```', body)
    raw_mermaid = mmd_match.group(1).strip() if mmd_match else ""
    mermaid_code = re.sub(r'<!--[\s\S]*?-->', '', raw_mermaid).strip()

    # Extract Caption from *Hình ...* or _Hình ..._
    caption_match = re.search(r'[\*_](Hình\s*[^\*_\n]+)[\*_]', body)
    caption = caption_match.group(1).strip() if caption_match else f"Hình {fig_id}: {title}"

    # Extract Alt text: from explicit blockquote, or from Markdown image ![alt text](path)
    alt_match = re.search(
        r'>\s*\*\*(?:Mô tả trực quan|Mô tả|Alt text)\s*\(?Alt text\)?:\*\*\s*([^\n]+)',
        body,
        re.IGNORECASE,
    )
    if alt_match:
        alt_text = alt_match.group(1).strip()
    else:
        img_alt_match = re.search(r'!\[([^\]]{10,})\]', body)
        alt_text = img_alt_match.group(1).strip() if img_alt_match else title

    # Extract Educational purpose
    purpose_match = re.search(
        r'>\s*\*\*(?:Mục tiêu giáo dục|Mục đích|Educational purpose):\*\*\s*([^\n]+)',
        body,
        re.IGNORECASE,
    )
    educational_purpose = purpose_match.group(1).strip() if purpose_match else f"Làm rõ nội dung cho {title}"

    # Extract Related learning objective
    obj_match = re.search(
        r'>\s*\*\*(?:Mục tiêu bài học liên quan|Learning objective):\*\*\s*([^\n]+)',
        body,
        re.IGNORECASE,
    )
    related_objective = obj_match.group(1).strip() if obj_match else "Nắm vững nguyên lý trọng tâm"

    # Extract Provenance class
    prov_match = re.search(
        r'>\s*\*\*(?:Xuất xứ học liệu|Nguồn & Xuất xứ|Provenance)\s*\(?Provenance\)?:\*\*\s*(?:`|\[)?([A-Z_]+)(?:`|\])?',
        body,
        re.IGNORECASE,
    )
    provenance_class = "PEDAGOGICAL_RECONSTRUCTION"
    if prov_match:
        cand = prov_match.group(1).strip().upper()
        if cand in PROVENANCE_CLASSES:
            provenance_class = cand

    # Extract Source locators
    loc_match = re.findall(r'\[\s*(\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?)\s*\]', body)
    valid_locators = []
    for loc in loc_match:
        parts = re.split(r'[-\s–]+', loc)
        for p in parts:
            p_clean = p.strip()
            if re.match(r'^\d{1,2}:\d{2}$', p_clean) and p_clean not in valid_locators:
                valid_locators.append(p_clean)
    source_locators = valid_locators if valid_locators else ["00:01"]

    # Extract rendered_asset_path if markdown image is present
    img_path_match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', body)
    rendered_path = img_path_match.group(1).strip() if img_path_match else None

    # Infer visual type
    visual_type = _infer_visual_type_from_mermaid(mermaid_code) if mermaid_code else "CONCEPT_MAP"

    fig_data = {
        "figure_id": fig_id,
        "title": title,
        "visual_type": visual_type,
        "educational_purpose": educational_purpose,
        "related_learning_objective": related_objective,
        "source_locators": source_locators,
        "provenance_class": provenance_class,
        "alt_text": alt_text,
        "caption": caption,
        "mermaid_code": mermaid_code,
        "rendering_status": "RENDER_NOT_VERIFIED",
        "is_untracked": False,
    }
    if rendered_path:
        fig_data["rendered_asset_path"] = rendered_path

    return fig_data


def _infer_visual_type_from_mermaid(code: str) -> str:
    """Infers visual type from Mermaid keyword starter."""
    code_lower = code.lower().strip()
    if code_lower.startswith("sequencediagram"):
        return "SEQUENCE_DIAGRAM"
    if code_lower.startswith("timeline"):
        return "TIMELINE"
    if code_lower.startswith("pie") or code_lower.startswith("xychart"):
        return "DATA_CHART"
    if (
        " vs " in code_lower
        or "so sánh" in code_lower
        or "left side" in code_lower
        or "right side" in code_lower
        or "leftside" in code_lower
        or "rightside" in code_lower
        or "vế trái" in code_lower
        or "vế phải" in code_lower
        or "ưu tiên hơn" in code_lower
    ):
        return "COMPARISON_DIAGRAM"
    if code_lower.startswith("flowchart"):
        return "FLOWCHART"
    if code_lower.startswith("graph"):
        if "-->" in code and ("q1" in code_lower or "quy trình" in code_lower or "bước" in code_lower or "step" in code_lower):
            return "FLOWCHART"
        return "CONCEPT_MAP"
    return "CONCEPT_MAP"


def is_safe_asset_path(path: str, base_dir: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Validates that a path is relative, contains no traversal segments, and stays within base_dir.
    
    Prevents:
    1. Absolute paths (e.g. /etc/passwd or C:\\...)
    2. Path traversal sequences ('..' in path components)
    3. Symlink escapes pointing outside base_dir
    4. Canonical path resolution escaping base_dir
    """
    if not path or not path.strip():
        return False, "Path is empty"

    clean = path.strip()

    # 1. Reject absolute paths
    if os.path.isabs(clean) or clean.startswith(("/", "\\")):
        return False, f"Path must be relative, not absolute: '{clean}'"

    # Check for Windows drive letters (e.g. C:)
    if len(clean) >= 2 and clean[1] == ":" and clean[0].isalpha():
        return False, f"Path must be relative, not absolute: '{clean}'"

    # 2. Reject path traversal tokens ('..')
    normalized_parts = [p for p in clean.replace("\\", "/").split("/") if p]
    if ".." in normalized_parts:
        return False, f"Path traversal ('..') detected: '{clean}'"

    # 3. Canonical resolution and symlink containment if base_dir is provided
    if base_dir:
        try:
            canonical_base = os.path.realpath(os.path.abspath(base_dir))
            full_path = os.path.join(base_dir, clean)
            canonical_target = os.path.realpath(os.path.abspath(full_path))

            # Target or its parent must be inside canonical_base or course root
            common = os.path.commonpath([canonical_base, canonical_target])
            if common != canonical_base:
                # Check if base_dir is a module subdirectory and target is safely contained in course root
                curr = canonical_base
                course_root = None
                while curr != os.path.dirname(curr):
                    if os.path.exists(os.path.join(curr, "assets")) and (
                        os.path.exists(os.path.join(curr, "manifest.json")) or os.path.exists(os.path.join(curr, "modules"))
                    ):
                        course_root = curr
                        break
                    curr = os.path.dirname(curr)
                if not course_root or os.path.commonpath([course_root, canonical_target]) != course_root:
                    return False, f"Path canonical target escapes base directory: '{clean}'"
        except Exception as e:
            return False, f"Path safety verification failed: {e}"

    return True, None


def validate_figure_properties(figure: Dict[str, Any]) -> List[str]:
    """Validates that a figure specification conforms to quality and safety requirements."""
    errors = []
    fig_id = figure.get("figure_id", "")
    if not fig_id or not re.match(r'^[a-zA-Z0-9_-]+$', fig_id):
        errors.append(f"Figure missing valid figure_id: '{fig_id}'")

    title = figure.get("title", "").strip()
    if len(title) < 3:
        errors.append(f"[{fig_id}] Title too short (< 3 chars): '{title}'")

    v_type = figure.get("visual_type")
    if v_type not in SUPPORTED_VISUAL_TYPES:
        errors.append(f"[{fig_id}] Unsupported visual_type: '{v_type}'. Allowed: {SUPPORTED_VISUAL_TYPES}")

    p_class = figure.get("provenance_class")
    if p_class not in PROVENANCE_CLASSES:
        errors.append(f"[{fig_id}] Unsupported provenance_class: '{p_class}'. Allowed: {PROVENANCE_CLASSES}")

    locators = figure.get("source_locators", [])
    if not locators:
        errors.append(f"[{fig_id}] Missing source_locators")

    alt_text = figure.get("alt_text", "").strip()
    if len(alt_text) < 10:
        errors.append(f"[{fig_id}] Alt text missing or too brief (< 10 chars)")

    caption = figure.get("caption", "").strip()
    if len(caption) < 10:
        errors.append(f"[{fig_id}] Caption missing or too brief (< 10 chars)")

    # Safe path validation for rendered or source spec paths
    for p_key in ("source_spec_path", "rendered_asset_path"):
        path_val = figure.get(p_key)
        if path_val:
            safe, reason = is_safe_asset_path(path_val)
            if not safe:
                errors.append(f"[{fig_id}] {reason}")

    # Mermaid syntax check if mermaid code present
    mmd_code = figure.get("mermaid_code", "").strip()
    if mmd_code:
        first_line = mmd_code.split("\n")[0].strip().lower()
        first_word = first_line.split()[0] if first_line.split() else ""
        if first_word not in VALID_MERMAID_TYPES:
            errors.append(f"[{fig_id}] Invalid or unsupported Mermaid starter: '{first_word}'")

    return errors


def validate_chart_fidelity(figure: Dict[str, Any], raw_source_content: str) -> List[str]:
    """Guards against fabricated data charts or quantitative values absent from raw source."""
    violations = []
    fig_id = figure.get("figure_id", "FIG")
    v_type = figure.get("visual_type")
    mmd = figure.get("mermaid_code", "")

    # If visual_type is DATA_CHART or Mermaid uses pie/xychart
    if v_type == "DATA_CHART" or re.search(r'^\s*(pie|xychart)', mmd, re.MULTILINE):
        # Extract numerical percentages or counts from diagram
        matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', mmd) + re.findall(r':\s*(\d+(?:\.\d+)?)', mmd)
        for num_str in matches:
            if num_str not in raw_source_content:
                violations.append(
                    f"[{fig_id}] Fabricated quantitative chart data detected: value '{num_str}' "
                    f"does not exist in raw source material."
                )

    return violations


class VisualAssetManager:
    """Manages diagram file persistence, local mmdc rendering, and visual manifest generation."""

    def __init__(
        self,
        assets_dir: str,
        mmdc_binary: Optional[str] = None,
        puppeteer_config: Optional[str] = None,
        automatic: bool = False,
    ):
        self.automatic = automatic
        self.assets_dir = assets_dir
        self.mmdc_binary = mmdc_binary or shutil.which("mmdc")
        self.puppeteer_config = puppeteer_config or self._find_puppeteer_config()
        os.makedirs(self.assets_dir, exist_ok=True)

    def _find_puppeteer_config(self) -> Optional[str]:
        """Locates minimal Puppeteer configuration if Chrome/Chromium is installed."""
        cfg_path = os.path.join(os.path.dirname(__file__), "puppeteer-config.json")
        if os.path.exists(cfg_path):
            return cfg_path
        if os.path.exists("/tmp/puppeteer-config.json"):
            return "/tmp/puppeteer-config.json"
        return None

    def is_renderer_available(self) -> bool:
        """Returns True if a functional Mermaid CLI renderer is found."""
        return bool(self.mmdc_binary and os.path.exists(self.mmdc_binary) and os.access(self.mmdc_binary, os.X_OK))

    def process_figures_for_lesson(
        self,
        lesson_id: str,
        figures: List[Dict[str, Any]],
        raw_source_content: str = "",
    ) -> Tuple[List[Dict[str, Any]], str, str]:
        """Saves .mmd files, renders to .svg if renderer is available, and writes visual_manifest.json.
        
        Returns:
            Tuple of (processed_figures, manifest_path, manifest_sha256)
        """
        lesson_assets_dir = os.path.join(self.assets_dir, lesson_id)
        os.makedirs(lesson_assets_dir, exist_ok=True)

        processed = []
        renderer_avail = self.is_renderer_available()

        for fig in figures:
            fig_copy = dict(fig)
            fig_id = fig_copy.get("figure_id", "F01")
            if not re.fullmatch(r"[A-Za-z0-9_-]+", fig_id):
                raise ValueError("Unsafe figure ID")
            if self.automatic:
                fig_copy["visual_review_status"] = "VISUAL_LAYOUT_NOT_VERIFIED"
                fig_copy["visual_review_notes"] = "Pending human visual review; static checks do not establish suitability."
            slug = slugify(fig_copy.get("title", fig_id))

            # Spec status validation
            spec_errors = validate_figure_properties(fig_copy)
            fig_copy["spec_status"] = "SPEC_VALID" if not spec_errors else "SPEC_INVALID"

            mmd_code = fig_copy.get("mermaid_code", "").strip()
            if self.automatic and re.search(r"<\s*(?:img|image|script)|@\{[^}]*img\s*:|https?://|data:image", mmd_code, re.I):
                raise ValueError("Automatic diagrams cannot embed images, scripts or external URLs")
            if mmd_code:
                # 1. Save .mmd file
                mmd_filename = f"{fig_id}_{slug}.mmd"
                mmd_path = os.path.join(lesson_assets_dir, mmd_filename)
                mmd_bytes = (mmd_code + "\n").encode("utf-8")
                with open(mmd_path, "wb") as f:
                    f.write(mmd_bytes)

                mmd_sha = calculate_sha256_bytes(mmd_bytes)
                fig_copy["source_spec_path"] = os.path.join("assets", lesson_id, mmd_filename)
                fig_copy["source_spec_sha256"] = mmd_sha

                # 2. Attempt SVG render if renderer available
                svg_filename = f"{fig_id}_{slug}.svg"
                svg_path = os.path.join(lesson_assets_dir, svg_filename)

                if renderer_avail:
                    rendered, status, svg_sha = self._render_mermaid_file(mmd_path, svg_path)
                    fig_copy["rendering_status"] = status
                    if rendered and svg_sha:
                        fig_copy["rendered_asset_path"] = os.path.join("assets", lesson_id, svg_filename)
                        fig_copy["rendered_asset_sha256"] = svg_sha
                    else:
                        fig_copy["rendered_asset_path"] = None
                        fig_copy["rendered_asset_sha256"] = None
                else:
                    fig_copy["rendering_status"] = "RENDER_NOT_VERIFIED"
                    fig_copy["rendered_asset_path"] = None
                    fig_copy["rendered_asset_sha256"] = None
            else:
                if fig_copy.get("visual_type") == "IMAGE_ASSET_REQUIRED":
                    fig_copy["rendering_status"] = "IMAGE_ASSET_REQUIRED"
                else:
                    fig_copy["rendering_status"] = "RENDER_NOT_VERIFIED"

            # Visual review status separation
            v_status = fig_copy.get("visual_review_status")
            if v_status not in VISUAL_REVIEW_STATUSES:
                fig_copy["visual_review_status"] = "VISUAL_LAYOUT_NOT_VERIFIED"
            if "visual_review_notes" not in fig_copy or not fig_copy["visual_review_notes"]:
                if fig_copy["visual_review_status"] == "VISUAL_REVIEWED":
                    fig_copy["visual_review_notes"] = "Visual layout and text legibility verified without clipping."
                else:
                    fig_copy["visual_review_notes"] = "Requires visual layout inspection of rendered SVG asset."

            processed.append(fig_copy)

        # 3. Save visual_manifest.json
        all_spec_valid = all(f.get("spec_status") == "SPEC_VALID" for f in processed)
        all_render_verified = bool(processed and all(f.get("rendering_status") == "RENDER_VERIFIED" for f in processed))
        all_visual_reviewed = bool(processed and all(f.get("visual_review_status") == "VISUAL_REVIEWED" for f in processed))

        manifest_path = os.path.join(lesson_assets_dir, "visual_manifest.json")
        manifest_data = {
            "lesson_id": lesson_id,
            "total_figures": len(processed),
            "renderer_available": renderer_avail,
            "renderer_binary": self.mmdc_binary if renderer_avail else "NONE",
            "quality_rubric_version": QUALITY_RUBRIC_VERSION,
            "visual_acceptance_summary": {
                "spec_valid": all_spec_valid,
                "render_verified": all_render_verified,
                "visual_reviewed": all_visual_reviewed,
                "content_quality_accepted": False,
            },
            "figures": processed,
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        manifest_sha256 = calculate_sha256_bytes(
            json.dumps(manifest_data, indent=2, ensure_ascii=False).encode("utf-8")
        )

        return processed, manifest_path, manifest_sha256

    def _render_mermaid_file(self, mmd_path: str, svg_path: str) -> Tuple[bool, str, Optional[str]]:
        """Invokes mmdc to render SVG and validates output."""
        if not self.is_renderer_available():
            return False, "RENDER_UNAVAILABLE", None

        try:
            cmd = [str(self.mmdc_binary)]
            if self.puppeteer_config and os.path.exists(self.puppeteer_config):
                cmd.extend(["-p", self.puppeteer_config])
            cmd.extend(["-i", mmd_path, "-o", svg_path])
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if res.returncode == 0 and os.path.exists(svg_path):
                # Verify valid non-empty SVG file
                with open(svg_path, "rb") as sf:
                    svg_bytes = sf.read()
                if len(svg_bytes) > 20 and b"<svg" in svg_bytes:
                    return True, "RENDER_VERIFIED", calculate_sha256_bytes(svg_bytes)
                else:
                    return False, "RENDER_FAILED", None
            else:
                logger.warning(f"mmdc failed: {res.stderr.decode('utf-8', errors='ignore')}")
                return False, "RENDER_FAILED", None
        except Exception as e:
            logger.error(f"Error rendering mermaid file {mmd_path}: {e}")
            return False, "RENDER_FAILED", None

    @staticmethod
    def verify_manifest_assets(manifest_path: str, base_dir: Optional[str] = None) -> List[str]:
        """Validates that all assets declared in a visual manifest exist on disk and match hashes."""
        errors = []
        if not os.path.exists(manifest_path):
            return [f"Manifest not found: {manifest_path}"]

        if base_dir is None:
            # Assume base_dir is fixtures directory or parent of assets
            manifest_dir = os.path.dirname(os.path.abspath(manifest_path))
            base_dir = os.path.dirname(os.path.dirname(manifest_dir))

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        for fig in manifest_data.get("figures", []):
            fid = fig.get("figure_id", "FIG")

            # 1. Verify source spec (.mmd)
            spec_rel = fig.get("source_spec_path")
            expected_spec_sha = fig.get("source_spec_sha256")
            if spec_rel:
                safe, reason = is_safe_asset_path(spec_rel, base_dir=base_dir)
                if not safe:
                    errors.append(f"[{fid}] Unsafe source spec path: {reason}")
                else:
                    spec_full = os.path.join(base_dir, spec_rel)
                    if not os.path.exists(spec_full):
                        errors.append(f"[{fid}] Missing source spec file: {spec_rel}")
                    elif expected_spec_sha:
                        with open(spec_full, "rb") as sf:
                            actual_sha = calculate_sha256_bytes(sf.read())
                        if actual_sha != expected_spec_sha:
                            errors.append(
                                f"[{fid}] Source spec hash mismatch: expected {expected_spec_sha}, got {actual_sha}"
                            )

            # 2. Verify rendered asset (.svg)
            rendered_rel = fig.get("rendered_asset_path")
            expected_rendered_sha = fig.get("rendered_asset_sha256")
            if rendered_rel:
                safe, reason = is_safe_asset_path(rendered_rel, base_dir=base_dir)
                if not safe:
                    errors.append(f"[{fid}] Unsafe rendered asset path: {reason}")
                else:
                    rendered_full = os.path.join(base_dir, rendered_rel)
                    if not os.path.exists(rendered_full):
                        errors.append(f"[{fid}] Missing rendered asset file: {rendered_rel}")
                    else:
                        with open(rendered_full, "rb") as rf:
                            svg_bytes = rf.read()
                        if len(svg_bytes) <= 20 or b"<svg" not in svg_bytes:
                            errors.append(f"[{fid}] Rendered asset is corrupt or not valid SVG: {rendered_rel}")
                        elif expected_rendered_sha:
                            actual_sha = calculate_sha256_bytes(svg_bytes)
                            if actual_sha != expected_rendered_sha:
                                errors.append(
                                    f"[{fid}] Rendered asset hash mismatch: expected {expected_rendered_sha}, got {actual_sha}"
                                )

        return errors


def normalize_mermaid_code(code_or_bytes: Union[str, bytes]) -> str:
    """Normalizes Mermaid diagram code for deterministic semantic comparison.
    
    - Handles bytes or string input.
    - Strips embedded HTML comments (<!-- ... -->).
    - Standardizes line endings (CRLF/CR -> LF).
    - Strips trailing whitespace per line.
    - Strips leading and trailing blank lines (handling pipeline's trailing newline convention).
    - Preserves internal indentation, node labels, and diagram topology.
    """
    if isinstance(code_or_bytes, bytes):
        text = code_or_bytes.decode("utf-8", errors="replace")
    else:
        text = str(code_or_bytes)

    # Strip HTML comments that may be embedded in markdown blocks
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    # Standardize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in text.split("\n")]
    # Strip leading and trailing empty lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).strip()


def validate_figure_semantic_binding(
    markdown_content: str,
    manifest_data: Dict[str, Any],
    resolve_path_fn: Optional[Callable[[str], str]] = None,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validates figure identity and source-content binding between audited Markdown and visual manifest.
    
    Enforces:
    1. Figure count equivalence between Markdown and visual manifest.
    2. Strict figure ID uniqueness and one-to-one mapping (no missing, extra, or duplicate IDs).
    3. Source spec (.mmd) existence and SHA256 integrity on disk.
    4. Mermaid content semantic equivalence between normalized Markdown and disk .mmd source bytes.
    5. Rendered asset (.svg) existence, validity, and SHA256 integrity on disk.
    6. Nonvisual lesson compatibility (0 figures in markdown and 0 in manifest returns valid).
    
    Returns:
        Tuple of (is_valid: bool, error_category: Optional[str], error_message: Optional[str])
    """
    if resolve_path_fn is None:
        resolve_path_fn = lambda p: p

    # 1. Figure marker integrity check
    marker_errors = check_figure_markers(markdown_content)
    if marker_errors:
        return (
            False,
            "VISUAL_MARKER_MALFORMED",
            f"Malformed or mismatched figure markers: {'; '.join(marker_errors)}",
        )

    md_figures = extract_figures_from_markdown(markdown_content)
    manifest_figures = manifest_data.get("figures", []) if manifest_data else []

    # 2. Check for untracked figures in Markdown
    untracked = [
        f for f in md_figures
        if f.get("is_untracked") or str(f.get("figure_id", "")).startswith("UNTRACKED")
    ]
    if untracked:
        untracked_ids = [f.get("figure_id") for f in untracked]
        return (
            False,
            "VISUAL_UNTRACKED_FIGURE",
            f"Untracked visual content detected in Markdown: {untracked_ids}",
        )

    # Nonvisual lesson compatibility: 0 figures in markdown and 0 in manifest
    if len(md_figures) == 0 and len(manifest_figures) == 0:
        return True, None, None

    # Figure count check
    if len(md_figures) != len(manifest_figures):
        return (
            False,
            "VISUAL_FIGURES_MISMATCH",
            f"Figure count mismatch: markdown contains {len(md_figures)} figure(s), "
            f"but visual manifest contains {len(manifest_figures)} figure(s)",
        )

    # Validate figure IDs in Markdown
    md_ids: List[str] = []
    for fig in md_figures:
        fid = fig.get("figure_id")
        if not fid or not str(fid).strip():
            return False, "VISUAL_FIGURE_ID_MISMATCH", "Figure in Markdown is missing figure_id"
        md_ids.append(str(fid).strip())

    if len(md_ids) != len(set(md_ids)):
        return (
            False,
            "VISUAL_FIGURE_ID_MISMATCH",
            f"Duplicate figure_id detected in Markdown figures: {md_ids}",
        )

    # Validate figure IDs in manifest
    manifest_ids: List[str] = []
    for fig in manifest_figures:
        fid = fig.get("figure_id")
        if not fid or not str(fid).strip():
            return False, "VISUAL_FIGURE_ID_MISMATCH", "Figure in visual manifest is missing figure_id"
        manifest_ids.append(str(fid).strip())

    if len(manifest_ids) != len(set(manifest_ids)):
        return (
            False,
            "VISUAL_FIGURE_ID_MISMATCH",
            f"Duplicate figure_id detected in visual manifest figures: {manifest_ids}",
        )

    # One-to-one figure ID set check
    if set(md_ids) != set(manifest_ids):
        missing = sorted(list(set(md_ids) - set(manifest_ids)))
        extra = sorted(list(set(manifest_ids) - set(md_ids)))
        return (
            False,
            "VISUAL_FIGURE_ID_MISMATCH",
            f"Figure ID mismatch between Markdown and manifest: missing in manifest: {missing}, extra in manifest: {extra}",
        )

    # Map figures by figure_id to support reordered figures cleanly
    md_by_id = {f["figure_id"].strip(): f for f in md_figures}
    manifest_by_id = {f["figure_id"].strip(): f for f in manifest_figures}

    for fig_id in manifest_ids:
        m_fig = manifest_by_id[fig_id]
        md_fig = md_by_id[fig_id]

        spec_rel = m_fig.get("source_spec_path")
        saved_spec_sha = m_fig.get("source_spec_sha256")
        md_mermaid = md_fig.get("mermaid_code", "")

        is_mermaid_figure = bool(
            (spec_rel and spec_rel.endswith(".mmd")) or (md_mermaid and md_mermaid.strip())
        )

        if is_mermaid_figure:
            if not spec_rel or not saved_spec_sha:
                return (
                    False,
                    "VISUAL_SPEC_MISSING",
                    f"Figure {fig_id} missing source spec path or sha256 in visual manifest",
                )

            normalized_spec_parts = [p for p in spec_rel.replace("\\", "/").split("/") if p]
            if ".." in normalized_spec_parts:
                return (
                    False,
                    "VISUAL_SPEC_MISSING",
                    f"Figure {fig_id} unsafe source spec path traversal: '{spec_rel}'",
                )

            full_spec_path = resolve_path_fn(spec_rel)
            if not os.path.exists(full_spec_path):
                return (
                    False,
                    "VISUAL_SPEC_MISSING",
                    f"Figure {fig_id} source spec missing on disk: {full_spec_path}",
                )

            with open(full_spec_path, "rb") as sf:
                disk_spec_bytes = sf.read()

            actual_spec_sha = calculate_sha256_bytes(disk_spec_bytes)
            if actual_spec_sha != saved_spec_sha:
                return (
                    False,
                    "VISUAL_SPEC_MODIFIED",
                    f"Figure {fig_id} source spec modified on disk: expected {saved_spec_sha}, got {actual_spec_sha}",
                )

            # Compare normalized Markdown mermaid_code with normalized disk .mmd source bytes
            norm_md = normalize_mermaid_code(md_mermaid)
            norm_disk = normalize_mermaid_code(disk_spec_bytes)
            if norm_md != norm_disk:
                return (
                    False,
                    "VISUAL_SOURCE_CONTENT_MISMATCH",
                    f"Figure {fig_id} Mermaid content mismatch between Markdown and manifest source spec",
                )
        else:
            # External-image-only figure: if source_spec_path is provided, verify it
            if spec_rel:
                normalized_spec_parts = [p for p in spec_rel.replace("\\", "/").split("/") if p]
                if ".." in normalized_spec_parts:
                    return (
                        False,
                        "VISUAL_SPEC_MISSING",
                        f"Figure {fig_id} unsafe source spec path traversal: '{spec_rel}'",
                    )
                full_spec_path = resolve_path_fn(spec_rel)
                if not os.path.exists(full_spec_path):
                    return (
                        False,
                        "VISUAL_SPEC_MISSING",
                        f"Figure {fig_id} source spec missing on disk: {full_spec_path}",
                    )
                if saved_spec_sha:
                    with open(full_spec_path, "rb") as sf:
                        actual_spec_sha = calculate_sha256_bytes(sf.read())
                    if actual_spec_sha != saved_spec_sha:
                        return (
                            False,
                            "VISUAL_SPEC_MODIFIED",
                            f"Figure {fig_id} source spec modified on disk: expected {saved_spec_sha}, got {actual_spec_sha}",
                        )

        # Rendered asset verification
        rendered_rel = m_fig.get("rendered_asset_path")
        saved_rendered_sha = m_fig.get("rendered_asset_sha256")
        rendering_status = m_fig.get("rendering_status")

        if rendering_status == "RENDER_VERIFIED" or rendered_rel:
            if not rendered_rel or not saved_rendered_sha:
                return (
                    False,
                    "VISUAL_ASSET_MISSING",
                    f"Figure {fig_id} marked RENDER_VERIFIED but missing rendered asset path or sha256",
                )

            normalized_rendered_parts = [p for p in rendered_rel.replace("\\", "/").split("/") if p]
            if ".." in normalized_rendered_parts:
                return (
                    False,
                    "VISUAL_ASSET_MISSING",
                    f"Figure {fig_id} unsafe rendered asset path traversal: '{rendered_rel}'",
                )

            full_rendered_path = resolve_path_fn(rendered_rel)
            if not os.path.exists(full_rendered_path):
                return (
                    False,
                    "VISUAL_ASSET_MISSING",
                    f"Figure {fig_id} rendered asset missing on disk: {full_rendered_path}",
                )

            with open(full_rendered_path, "rb") as rf:
                svg_bytes = rf.read()

            if len(svg_bytes) <= 20 or b"<svg" not in svg_bytes:
                return (
                    False,
                    "VISUAL_ASSET_MODIFIED",
                    f"Figure {fig_id} rendered asset is corrupt or not valid SVG: {full_rendered_path}",
                )

            actual_rendered_sha = calculate_sha256_bytes(svg_bytes)
            if actual_rendered_sha != saved_rendered_sha:
                return (
                    False,
                    "VISUAL_ASSET_MODIFIED",
                    f"Figure {fig_id} rendered asset modified on disk: expected {saved_rendered_sha}, got {actual_rendered_sha}",
                )

    return True, None, None


def normalize_markdown_asset_paths(
    content: str,
    figures_or_manifest: Union[Dict[str, Any], List[Dict[str, Any]]],
    lesson_id: Optional[str] = None,
) -> str:
    """Normalizes figure image asset paths in lesson Markdown to match rendered assets.
    
    Resolves figures strictly by figure_id (e.g. F01, F02), reconciling mismatched Worker
    English filename slugs with the actual rendered SVG assets (e.g. Vietnamese slugs).
    
    Guarantees:
    1. Idempotency: Running repeatedly on already-normalized content produces identical output.
    2. Exact Figure Binding: Resolves by figure_id, never guessing by arbitrary file names.
    3. Non-destructive: Leaves Mermaid code, titles, captions, and text content intact.
    """
    if isinstance(figures_or_manifest, dict):
        figures = figures_or_manifest.get("figures", [figures_or_manifest])
    else:
        figures = figures_or_manifest

    manifest_by_id: Dict[str, str] = {}
    for f in figures:
        fid = f.get("figure_id")
        rendered_path = f.get("rendered_asset_path")
        if fid and rendered_path:
            manifest_by_id[str(fid).strip()] = rendered_path

    if not manifest_by_id:
        return content

    # 1. First pass: explicit FIGURE_START: <fig_id> blocks
    pattern_explicit = re.compile(
        r'(<!--\s*FIGURE_START:\s*([a-zA-Z0-9_-]+)\s*-->)([\s\S]*?)(<!--\s*FIGURE_END:\s*\2\s*-->)',
        re.MULTILINE,
    )

    def _replace_block(match: re.Match) -> str:
        start_tag = match.group(1)
        fig_id = match.group(2).strip()
        body = match.group(3)
        end_tag = match.group(4)
        if fig_id in manifest_by_id:
            expected_path = manifest_by_id[fig_id]
            body = re.sub(
                r'(!\[[^\]]*\]\()([^)]+)(\))',
                lambda m: f'{m.group(1)}{expected_path}{m.group(3)}',
                body,
            )
            body = re.sub(
                r'(<img\s+[^>]*src=[\'"])([^\'"]+)([\'"][^>]*>)',
                lambda m: f'{m.group(1)}{expected_path}{m.group(3)}',
                body,
                flags=re.IGNORECASE,
            )
        return f'{start_tag}{body}{end_tag}'

    updated = pattern_explicit.sub(_replace_block, content)

    # 2. Second pass: Standalone figure image links if any remain outside explicit blocks
    for fig_id, expected_path in manifest_by_id.items():
        def _replace_standalone(m: re.Match) -> str:
            alt_text = m.group(1)
            old_path = m.group(2)
            is_match = False
            if re.search(r'assets/[^/]+/' + re.escape(fig_id) + r'_[^)]+', old_path):
                is_match = True
            elif re.search(r'\b' + re.escape(fig_id) + r'\b', alt_text):
                is_match = True
            if is_match and old_path != expected_path:
                return f'![{alt_text}]({expected_path})'
            return m.group(0)

        updated = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', _replace_standalone, updated)

    return updated



def validate_automatic_visuals(content, visuals, output_dir):
    """Only locally rendered, manifest-bound diagrams may enter automatic production."""
    import xml.etree.ElementTree as ET
    issues = []
    figures = extract_figures_from_markdown(content)
    manifest_figures = visuals.get("figures", [])
    if len(figures) != len(manifest_figures):
        issues.append("Automatic visual manifest figure count mismatch")
    if figures:
        path = visuals.get("manifest_path")
        if not path or not os.path.isfile(path):
            return issues + ["Missing automatic visual manifest"]
        with open(path, "rb") as mf:
            if hashlib.sha256(mf.read()).hexdigest() != visuals.get("manifest_sha256"):
                issues.append("Automatic visual manifest checksum mismatch")
        issues.extend(VisualAssetManager.verify_manifest_assets(path, base_dir=output_dir))
    allowed = set()
    for fig in manifest_figures:
        path = fig.get("rendered_asset_path")
        if not path or fig.get("rendering_status") != "RENDER_VERIFIED":
            issues.append("Automatic visual render is not verified")
            continue
        allowed.add(path)
        full_path = os.path.realpath(os.path.join(output_dir, path))
        if os.path.commonpath([os.path.realpath(output_dir), full_path]) != os.path.realpath(output_dir):
            issues.append("Automatic visual path escapes output directory")
            continue
        try:
            root = ET.parse(full_path).getroot()
            if not root.tag.endswith("svg") or any(
                node.tag.rsplit("}", 1)[-1].lower() in ("image", "img", "script", "iframe", "video", "use")
                for node in root.iter()
            ):
                issues.append("PROHIBITED_INSTRUCTOR_IMAGE: Embedded media is forbidden in automatic SVGs")
        except (OSError, ET.ParseError):
            issues.append("Invalid automatic SVG")
    references = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content)
    references += re.findall(r'<img\s+[^>]*src=[\'"]([^\'"]+)[\'"]', content, re.I)
    if (any(p not in allowed for p in references)
        or re.search(r'!\[[^\]\n]*\](?!\()', content)
        or re.search(r'<(?:img|iframe|video|object|embed|svg|style|link)\b', content, re.I)):
        issues.append("PROHIBITED_INSTRUCTOR_IMAGE: Automatic images must be rendered diagrams bound to the visual manifest")
    return issues
