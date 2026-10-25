"""Calibration Fixture for M01-L07: The four values of the Agile Manifesto.

Used as a deterministic design fixture and test baseline for Visual Learning Design.
Does NOT call AGY live.
"""

import json
import os
from typing import Any, Dict


def get_m01_l07_draft_markdown() -> str:
    """Returns the calibrated visual-first lesson Markdown for M01-L07."""
    path = os.path.join(os.path.dirname(__file__), "M01_L07_lesson_draft.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_m01_l07_audit_report() -> Dict[str, Any]:
    """Returns the calibrated audit report JSON for M01-L07."""
    path = os.path.join(os.path.dirname(__file__), "M01_L07_audit_report.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_m01_l07_visual_manifest() -> Dict[str, Any]:
    """Returns the calibrated visual manifest JSON for M01-L07."""
    path = os.path.join(os.path.dirname(__file__), "assets", "M01-L07", "visual_manifest.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_m01_l07_rendered_svg_paths() -> Dict[str, str]:
    """Returns local filesystem paths to the rendered SVG assets for M01-L07."""
    base_dir = os.path.join(os.path.dirname(__file__), "assets", "M01-L07")
    return {
        "F01": os.path.join(base_dir, "F01_b_n_c_p_gi_tr_c_t_l_i_c_a_tuy_n_ng_n_agi.svg"),
        "F02": os.path.join(base_dir, "F02_v_ng_l_p_th_ch_ng_v_c_n_b_ng_k_ho_ch_tro.svg"),
    }
