"""Shared deterministic baseline and prohibited-image policy. No provider imports."""

import os
import re
from typing import List, Optional

APPROVED_BASELINES = {
    "M02-L11": {
        "lesson_id": "M02-L11",
        "decision": "APPROVED",
        "human_review_score": "91/100",
        "approved_final_sha256": "e923d81138a29fbae7295221d0d99fa5954c3554d8f13cc2a060dad9014221cf",
        "visual_manifest_sha256": "d27ff076c9072f6c41ac8e88528386e89c6458fd004524c83b4f23c8689f0366",
        "acceptance_artifact": "generated_course/Agile_Project_Management/evidence/checkpoints/acceptance/M02-L11_acceptance.json",
    },
    "M03-L08": {
        "lesson_id": "M03-L08",
        "decision": "APPROVED",
        "human_review_score": "93/100",
        "approved_final_sha256": "5df3b377944fb7d16dc50b0c0c1dd267c046beefcae5e30928bda3fb921bd48d",
        "source_status": "INCOMPLETE",
        "known_limitations": [
            "missing Coursera quiz options/answer keys",
            "unavailable official template",
            "no Mermaid diagrams",
        ],
        "acceptance_artifact": "generated_course/Agile_Project_Management/evidence/checkpoints/acceptance/M03-L08_acceptance.json",
    },
}

PROHIBITED_INSTRUCTOR_PATTERNS = [
    r'\b(?:instructor|lecturer|presenter|author|speaker)[_-]?(?:photo|portrait|headshot|avatar|image|screenshot|thumbnail|likeness)\b',
    r'\b(?:profile[_-]?photo|speaker[_-]?thumbnail|author[_-]?headshot|lecturer[_-]?screenshot)\b',
    r'\b(?:shraddha(?:[_-]?sahu)?)\b',
]


def scan_for_prohibited_instructor_images(
    content: str,
    asset_paths: Optional[List[str]] = None,
) -> List[str]:
    """Scans content and visual assets against the mandatory Global Rule:
    ABSOLUTELY NO IMAGES OF COURSE AUTHORS OR INSTRUCTORS.
    
    Prohibits identifiable photos, portraits, avatars, headshots, thumbnails,
    lecturer screenshots, and stylized likenesses.
    """
    violations: List[str] = []

    # 1. Check markdown image references
    img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)

    # 2. Check HTML <img> tags
    for m in re.finditer(r'<img\s+[^>]*src=[\'"]([^\'"]+)[\'"][^>]*>', content, re.IGNORECASE):
        tag_str = m.group(0)
        alt_m = re.search(r'alt=[\'"]([^\'"]*)[\'"]', tag_str, re.IGNORECASE)
        alt_val = alt_m.group(1) if alt_m else ""
        img_refs.append((alt_val, m.group(1)))

    for alt, path in img_refs:
        clean_path = path.strip()
        ref_text = f"{alt} {clean_path}".lower()
        for pat in PROHIBITED_INSTRUCTOR_PATTERNS:
            if re.search(pat, ref_text, re.IGNORECASE):
                violations.append(
                    f"PROHIBITED_INSTRUCTOR_IMAGE: Instructor or author photo/portrait detected in image reference: "
                    f"'{clean_path}' (alt: '{alt}')"
                )
                break

    # 3. Check referenced asset files on disk (e.g. SVGs, metadata)
    if asset_paths:
        for a_path in asset_paths:
            if not os.path.exists(a_path):
                continue
            fname_lower = os.path.basename(a_path).lower()
            for pat in PROHIBITED_INSTRUCTOR_PATTERNS:
                if re.search(pat, fname_lower, re.IGNORECASE):
                    violations.append(
                        f"PROHIBITED_INSTRUCTOR_IMAGE: Asset filename matches prohibited instructor pattern: '{a_path}'"
                    )
                    break
            # If SVG, inspect internal elements
            if a_path.endswith(".svg"):
                try:
                    with open(a_path, "r", encoding="utf-8") as sf:
                        svg_text = sf.read().lower()
                    for pat in PROHIBITED_INSTRUCTOR_PATTERNS:
                        if re.search(pat, svg_text, re.IGNORECASE):
                            violations.append(
                                f"PROHIBITED_INSTRUCTOR_IMAGE: SVG asset contains prohibited instructor text/image: '{a_path}'"
                            )
                            break
                except Exception:
                    pass

    return violations

