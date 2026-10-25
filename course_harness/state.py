"""State, Resume, and Checkpoint Manager for Course Harness.

Maintains lesson lifecycle:
  PENDING -> DRAFTED -> AUDITED -> REPAIRING -> PASS / NEEDS_HUMAN_REVIEW / BLOCKED

Tracks source hashes, prompt/config version hashes, model pinning metadata,
attempt counts, verdict history, and checksums for full resumability.
"""

import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from course_harness.visual import (
    check_figure_markers,
    extract_figures_from_markdown,
    normalize_mermaid_code,
    validate_figure_semantic_binding,
)

# Keep archived provider code outside the deterministic/native import path.
EVIDENCE_CLASS = "REAL_GEMINI_API_VERIFIED"


def verified_api_receipt(receipt):
    if receipt.get("execution_mode") != "gemini_api":
        return False
    from course_harness.gemini_adapter import verified_api_receipt as verify
    return verify(receipt)


logger = logging.getLogger("course_harness.state")

VALID_STATES = {
    "PENDING",
    "DRAFTED",
    "AUDITED",
    "REPAIRING",
    "PASS",
    "HUMAN_ACCEPTED",
    "NEEDS_HUMAN_REVIEW",
    "NEEDS_REAUDIT",
    "BLOCKED",
    "INVALIDATED",
    "MOCK_DRAFTED",
    "MOCK_AUDITED",
    "MOCK_PASS",
}

EVIDENCE_CLASSES = {
    "REAL_AGY_VERIFIED",
    EVIDENCE_CLASS,
    "MOCK_SIMULATED",
    "MANUAL_UNVERIFIED",
    "HUMAN_ACCEPTED",
}


def calculate_file_sha256(filepath: str) -> str:
    """Computes SHA256 checksum of a file without modifying it."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_prompt_config_hash(prompts_dir: str, config_path: str) -> str:
    """Computes a composite hash of all prompt templates and configuration."""
    hasher = hashlib.sha256()

    # Hash config file
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            hasher.update(f.read())

    # Hash prompt files in stable sorted order
    if os.path.isdir(prompts_dir):
        for fname in sorted(os.listdir(prompts_dir)):
            if fname.endswith(".md"):
                p = os.path.join(prompts_dir, fname)
                with open(p, "rb") as f:
                    hasher.update(fname.encode("utf-8"))
                    hasher.update(f.read())

    return hasher.hexdigest()[:16]


class StateManager:
    """Manages lesson states and checkpoints on disk."""

    def __init__(
        self,
        checkpoints_dir: str,
        prompt_config_hash: str,
        acceptance_dir: Optional[str] = None,
        schema_path: Optional[str] = None,
        receipts_dir: Optional[str] = None,
        manifest_path: Optional[str] = None,
    ):
        self.checkpoints_dir = checkpoints_dir
        self.prompt_config_hash = prompt_config_hash
        self.acceptance_dir = acceptance_dir or os.path.join(self.checkpoints_dir, "acceptance")
        self.receipts_dir = receipts_dir or os.path.join(self.checkpoints_dir, "receipts")
        self.schema_path = schema_path or "course_harness/schemas/audit.schema.json"
        self.manifest_path = manifest_path
        os.makedirs(self.checkpoints_dir, exist_ok=True)
        os.makedirs(self.acceptance_dir, exist_ok=True)
        os.makedirs(self.receipts_dir, exist_ok=True)

    def _get_manifest_path(self) -> Optional[str]:
        target_path = self.manifest_path
        if not target_path:
            candidate = os.path.normpath(os.path.join(self.checkpoints_dir, "..", "..", "manifest.json"))
            if os.path.exists(candidate):
                target_path = candidate
        if target_path and os.path.exists(target_path):
            return target_path
        return None

    def _get_manifest_lesson_meta(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Loads lesson metadata from manifest if manifest exists."""
        target_path = self._get_manifest_path()
        if target_path:
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    lessons = data.get("lessons")
                    if isinstance(lessons, dict) and lesson_id in lessons:
                        return lessons[lesson_id]
                    # Also check modules if legacy or nested
                    for mod in data.get("modules", []):
                        if isinstance(mod, dict):
                            for l in mod.get("lessons", []):
                                if isinstance(l, dict) and (l.get("id") == lesson_id or l.get("lesson_id") == lesson_id):
                                    return l
            except Exception as e:
                logger.warning(f"Failed to load manifest at {target_path}: {e}")
        return None

    def _resolve_asset_path(self, path: str, final_path: Optional[str] = None) -> str:
        """Resolves relative asset path against project or checkpoints directories."""
        if os.path.isabs(path) and os.path.exists(path):
            return path
        candidates = [
            os.path.dirname(os.path.dirname(self.checkpoints_dir)),
            os.path.dirname(self.checkpoints_dir),
            os.getcwd(),
        ]
        if final_path:
            candidates.append(os.path.dirname(final_path))
            candidates.append(os.path.dirname(os.path.dirname(final_path)))
        for base in candidates:
            cand = os.path.normpath(os.path.join(base, path))
            if os.path.exists(cand):
                return cand
        return path

    def _resolve_visual_manifest_path(self, lesson_id: str, final_path: Optional[str] = None) -> Optional[str]:
        """Attempts to locate visual_manifest.json on disk for a lesson."""
        candidates = []
        base_dirs = [
            os.path.dirname(os.path.dirname(self.checkpoints_dir)),
            os.path.dirname(self.checkpoints_dir),
            os.getcwd(),
        ]
        if final_path:
            base_dirs.append(os.path.dirname(final_path))
            base_dirs.append(os.path.dirname(os.path.dirname(final_path)))
        for base in base_dirs:
            candidates.append(os.path.join(base, "assets", lesson_id, "visual_manifest.json"))
            candidates.append(os.path.join(base, "output_course", "assets", lesson_id, "visual_manifest.json"))
            candidates.append(os.path.join(base, lesson_id, "visual_manifest.json"))
        for c in candidates:
            if os.path.exists(c):
                return os.path.normpath(c)
        return None

    def save_audit_receipt(self, receipt: Dict[str, Any]) -> str:
        """Persists a Controller invocation receipt for an Auditor execution atomically."""
        inv_id = receipt.get("invocation_id")
        if not inv_id or not str(inv_id).strip():
            raise ValueError("Audit receipt requires a non-empty invocation_id")
        safe_id = str(inv_id).replace("/", "_").replace("\\", "_")
        path = os.path.join(self.receipts_dir, f"{safe_id}.json")
        temp_path = f"{path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, path)
        return path

    def get_audit_receipt(self, invocation_id: str) -> Optional[Dict[str, Any]]:
        """Loads a persisted audit invocation receipt by invocation_id."""
        if not invocation_id or not str(invocation_id).strip():
            return None
        safe_id = str(invocation_id).replace("/", "_").replace("\\", "_")
        path = os.path.join(self.receipts_dir, f"{safe_id}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Corrupted receipt file for {invocation_id}: {e}")
            return None

    def _get_checkpoint_path(self, lesson_id: str) -> str:
        safe_id = lesson_id.replace("/", "_").replace("\\", "_")
        return os.path.join(self.checkpoints_dir, f"{safe_id}.json")

    def load_checkpoint(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Loads existing checkpoint for a lesson if present."""
        path = self._get_checkpoint_path(lesson_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Corrupted checkpoint for {lesson_id}: {e}")
            return None

    def initialize_lesson_state(
        self,
        lesson_id: str,
        source_sha256: str,
        model_id: str = "gemini-3.8-flash-high",
        effort: str = "high",
        execution_mode: Optional[str] = None,
        lesson_type: Optional[str] = None,
        source_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initializes or checks invalidation of state for a lesson."""
        m_meta = self._get_manifest_lesson_meta(lesson_id)
        if m_meta:
            lesson_type = lesson_type or m_meta.get("source_type")
            source_status = source_status or m_meta.get("status")

        existing = self.load_checkpoint(lesson_id)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if existing:
            if lesson_type and not existing.get("lesson_type"):
                existing["lesson_type"] = lesson_type
            if source_status and not existing.get("source_status"):
                existing["source_status"] = source_status
            # Mode switching check: mock checkpoints cannot persist into real execution mode
            existing_ev_class = existing.get("evidence_class")
            existing_status = existing.get("status")
            if (existing_status == "MOCK_PASS" or existing_ev_class == "MOCK_SIMULATED") and execution_mode in ("automated_cli", "manual_cli_handoff", "gemini_api"):
                logger.info(f"Mode switched from mock to real for {lesson_id}; resetting checkpoint.")
                existing["status"] = "PENDING"
                existing["evidence_class"] = None
                existing["repair_attempts"] = 0
                existing["draft_version"] = 0
                existing["updated_at"] = now
                self.save_checkpoint(lesson_id, existing)
                return existing

            # Legacy MOCK PASS masquerading as PASS must be invalidated immediately
            if existing_status == "PASS" and existing_ev_class == "MOCK_SIMULATED":
                logger.warning(f"Legacy mock PASS checkpoint detected for {lesson_id}; invalidating.")
                self._invalidate_pass(lesson_id, existing, "LEGACY_MOCK_PASS_REJECTED")
                return existing

            # Check source hash invalidation
            if existing.get("source_sha256") != source_sha256:
                logger.info(f"Source changed for {lesson_id}; resetting checkpoint.")
                existing["status"] = "PENDING"
                existing["source_sha256"] = source_sha256
                existing["repair_attempts"] = 0
                existing["draft_version"] = 0
                existing["visual_manifest_sha256"] = None
                existing["updated_at"] = now
                self.save_checkpoint(lesson_id, existing)
                return existing

            # Check prompt/config hash invalidation
            if existing.get("prompt_config_hash") != self.prompt_config_hash:
                logger.info(f"Config/prompts changed for {lesson_id}; resetting checkpoint.")
                existing["status"] = "PENDING"
                existing["prompt_config_hash"] = self.prompt_config_hash
                existing["repair_attempts"] = 0
                existing["visual_manifest_sha256"] = None
                existing["updated_at"] = now
                self.save_checkpoint(lesson_id, existing)
                return existing

            return existing

        # Create fresh checkpoint
        checkpoint = {
            "lesson_id": lesson_id,
            "status": "PENDING",
            "source_sha256": source_sha256,
            "prompt_config_hash": self.prompt_config_hash,
            "model_id": model_id,
            "effort": effort,
            "evidence_class": "MOCK_SIMULATED" if execution_mode == "mock" else None,
            "lesson_type": lesson_type,
            "source_status": source_status,
            "draft_version": 0,
            "audit_version": 0,
            "repair_attempts": 0,
            "verdict": None,
            "draft_path": None,
            "audit_path": None,
            "final_path": None,
            "final_sha256": None,
            "audit_sha256": None,
            "error_category": None,
            "history": [],
            "created_at": now,
            "updated_at": now,
        }
        self.save_checkpoint(lesson_id, checkpoint)
        return checkpoint

    def save_checkpoint(self, lesson_id: str, checkpoint_data: Dict[str, Any]) -> None:
        """Atomically saves checkpoint to disk."""
        checkpoint_data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        path = self._get_checkpoint_path(lesson_id)
        temp_path = f"{path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, path)

    def transition(
        self,
        lesson_id: str,
        new_status: str,
        updates: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Transitions lesson to a new state with audit history logging."""
        if new_status not in VALID_STATES:
            raise ValueError(f"Invalid state '{new_status}'. Allowed: {VALID_STATES}")

        chk = self.load_checkpoint(lesson_id) or {}
        old_status = chk.get("status", "UNKNOWN")

        chk["status"] = new_status
        if updates:
            chk.update(updates)

        if "history" not in chk:
            chk["history"] = []

        chk["history"].append({
            "from_status": old_status,
            "to_status": new_status,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "details": {k: v for k, v in (updates or {}).items() if k != "history"},
        })

        self.save_checkpoint(lesson_id, chk)
        return chk

    def is_resumable_pass(
        self,
        lesson_id: str,
        current_source_sha256: str,
        lesson_type: Optional[str] = None,
        source_status: Optional[str] = None,
    ) -> bool:
        """Returns True if the lesson has a verified PASS or valid HUMAN_ACCEPTED with matching hashes.
        Fails closed: if any hash, artifact, or evidence field is missing, null, empty, or mismatched,
        invalidates the status and returns False.
        """
        chk = self.load_checkpoint(lesson_id)
        if not chk:
            return False

        status = chk.get("status")
        if status not in ("PASS", "HUMAN_ACCEPTED"):
            return False

        if status == "HUMAN_ACCEPTED":
            return self._is_resumable_human_acceptance(lesson_id, chk, current_source_sha256)

        # 1. Source hash check
        saved_source_sha = chk.get("source_sha256")
        if not saved_source_sha or not isinstance(saved_source_sha, str) or not saved_source_sha.strip():
            logger.warning(f"[{lesson_id}] Source SHA256 missing/empty in PASS checkpoint. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "SOURCE_HASH_MISSING")
            return False

        if saved_source_sha != current_source_sha256:
            logger.warning(
                f"[{lesson_id}] Source SHA256 mismatch (saved: {saved_source_sha}, current: {current_source_sha256}). Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "SOURCE_MISMATCH")
            return False

        # 2. Config & prompt hash check
        saved_prompt_cfg = chk.get("prompt_config_hash")
        if not saved_prompt_cfg or not isinstance(saved_prompt_cfg, str) or not saved_prompt_cfg.strip():
            logger.warning(f"[{lesson_id}] Prompt/config hash missing/empty in PASS checkpoint. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "CONFIG_PROMPT_HASH_MISSING")
            return False

        if saved_prompt_cfg != self.prompt_config_hash:
            logger.warning(
                f"[{lesson_id}] Prompt/config hash mismatch (saved: {saved_prompt_cfg}, expected: {self.prompt_config_hash}). Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "CONFIG_PROMPT_CHANGED")
            return False

        # 3. Final path and final sha256 check
        final_path = chk.get("final_path")
        if not final_path or not isinstance(final_path, str) or not final_path.strip():
            logger.warning(f"[{lesson_id}] Final output path missing/empty in PASS checkpoint. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "FINAL_PATH_MISSING")
            return False

        if not os.path.exists(final_path):
            logger.warning(f"[{lesson_id}] Final output file missing on disk: {final_path}. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "FINAL_OUTPUT_MISSING")
            return False

        saved_final_sha = chk.get("final_sha256")
        if not saved_final_sha or not isinstance(saved_final_sha, str) or not saved_final_sha.strip():
            logger.warning(f"[{lesson_id}] Final output sha256 missing/empty in PASS checkpoint. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "FINAL_SHA256_MISSING")
            return False

        current_final_sha = calculate_file_sha256(final_path)
        if current_final_sha != saved_final_sha:
            logger.warning(
                f"[{lesson_id}] Final output hash mismatch (saved: {saved_final_sha}, current: {current_final_sha}). Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "FINAL_OUTPUT_MODIFIED")
            return False

        # 4. Audit path and audit sha256 check
        audit_path = chk.get("audit_path")
        if not audit_path or not isinstance(audit_path, str) or not audit_path.strip():
            logger.warning(f"[{lesson_id}] Audit report path missing/empty in PASS checkpoint. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_PATH_MISSING")
            return False

        if not os.path.exists(audit_path):
            logger.warning(f"[{lesson_id}] Audit report file missing on disk: {audit_path}. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_REPORT_MISSING")
            return False

        saved_audit_sha = chk.get("audit_sha256")
        if not saved_audit_sha or not isinstance(saved_audit_sha, str) or not saved_audit_sha.strip():
            logger.warning(f"[{lesson_id}] Audit report sha256 missing/empty in PASS checkpoint. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_SHA256_MISSING")
            return False

        current_audit_sha = calculate_file_sha256(audit_path)
        if current_audit_sha != saved_audit_sha:
            logger.warning(
                f"[{lesson_id}] Audit report hash mismatch (saved: {saved_audit_sha}, current: {current_audit_sha}). Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "AUDIT_REPORT_MODIFIED")
            return False

        # 5. Authoritative report contents & final SHA256 binding verification
        try:
            with open(audit_path, "r", encoding="utf-8") as af:
                report_data = json.load(af)
        except Exception as e:
            logger.warning(f"[{lesson_id}] Failed to parse audit report JSON: {e}. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_REPORT_PARSE_ERROR")
            return False

        if report_data.get("verdict") != "PASS":
            logger.warning(f"[{lesson_id}] Audit report verdict is '{report_data.get('verdict')}', not PASS. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_VERDICT_NOT_PASS")
            return False

        # Context verification across caller, manifest, checkpoint, and receipt
        m_meta = self._get_manifest_lesson_meta(lesson_id)
        if m_meta:
            m_type = m_meta.get("source_type")
            m_status = m_meta.get("status")
            if lesson_type and lesson_type != m_type:
                logger.warning(
                    f"[{lesson_id}] Caller lesson_type '{lesson_type}' does not match manifest '{m_type}'. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "LESSON_CONTEXT_MISMATCH")
                return False
            if source_status and source_status != m_status:
                logger.warning(
                    f"[{lesson_id}] Caller source_status '{source_status}' does not match manifest '{m_status}'. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "LESSON_CONTEXT_MISMATCH")
                return False
            if chk.get("lesson_type") and chk.get("lesson_type") != m_type:
                logger.warning(
                    f"[{lesson_id}] Checkpoint lesson_type '{chk.get('lesson_type')}' does not match manifest '{m_type}'. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "LESSON_CONTEXT_MISMATCH")
                return False
            if chk.get("source_status") and chk.get("source_status") != m_status:
                logger.warning(
                    f"[{lesson_id}] Checkpoint source_status '{chk.get('source_status')}' does not match manifest '{m_status}'. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "LESSON_CONTEXT_MISMATCH")
                return False
            verified_lesson_type = m_type
            verified_source_status = m_status
        else:
            if lesson_type and chk.get("lesson_type") and lesson_type != chk.get("lesson_type"):
                logger.warning(
                    f"[{lesson_id}] Caller lesson_type '{lesson_type}' does not match checkpoint '{chk.get('lesson_type')}'. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "LESSON_CONTEXT_MISMATCH")
                return False
            if source_status and chk.get("source_status") and source_status != chk.get("source_status"):
                logger.warning(
                    f"[{lesson_id}] Caller source_status '{source_status}' does not match checkpoint '{chk.get('source_status')}'. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "LESSON_CONTEXT_MISMATCH")
                return False
            verified_lesson_type = lesson_type or chk.get("lesson_type")
            verified_source_status = source_status or chk.get("source_status")

        # Also cross-check receipt context if receipt is available
        inv_id_chk = chk.get("audit_invocation_id")
        if inv_id_chk:
            rcpt = self.get_audit_receipt(str(inv_id_chk).strip())
            if rcpt:
                rcpt_type = rcpt.get("lesson_type")
                if rcpt_type:
                    if verified_lesson_type and rcpt_type != verified_lesson_type:
                        logger.warning(
                            f"[{lesson_id}] Receipt lesson_type '{rcpt_type}' != '{verified_lesson_type}'. Invalidating PASS."
                        )
                        self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_CONTEXT_MISMATCH")
                        return False
                    verified_lesson_type = verified_lesson_type or rcpt_type
                rcpt_status = rcpt.get("source_status")
                if rcpt_status:
                    if verified_source_status and rcpt_status != verified_source_status:
                        logger.warning(
                            f"[{lesson_id}] Receipt source_status '{rcpt_status}' != '{verified_source_status}'. Invalidating PASS."
                        )
                        self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_CONTEXT_MISMATCH")
                        return False
                    verified_source_status = verified_source_status or rcpt_status

        # Visual exemption authorization: trustworthy context requires authoritative manifest
        dim_scores = report_data.get("dimension_scores") or {}
        if dim_scores.get("VISUAL_PEDAGOGY") == "NOT_APPLICABLE":
            if not m_meta:
                logger.warning(
                    f"[{lesson_id}] Visual exemption claimed but authoritative manifest is missing/untrusted. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "UNTRUSTED_EXEMPTION_CONTEXT")
                return False
            if m_meta.get("source_type") not in ("QUIZ", "GLOSSARY") or m_meta.get("status") != "AVAILABLE":
                logger.warning(
                    f"[{lesson_id}] Visual exemption unauthorized for source_type='{m_meta.get('source_type')}', status='{m_meta.get('status')}'. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "UNAUTHORIZED_VISUAL_EXEMPTION")
                return False

        from course_harness.validator import is_production_quality_eligible
        q_eligible, q_reason = is_production_quality_eligible(
            report_data,
            lesson_type=verified_lesson_type,
            source_status=verified_source_status,
        )
        if not q_eligible:
            logger.warning(
                f"[{lesson_id}] Audit report failed production quality eligibility ({q_reason}). Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "QUALITY_ELIGIBILITY_FAILED")
            return False

        audited_final_sha = report_data.get("audited_final_sha256")
        if not audited_final_sha or not isinstance(audited_final_sha, str) or not audited_final_sha.strip():
            logger.warning(f"[{lesson_id}] Audit report lacks audited_final_sha256 binding. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_BINDING_MISSING")
            return False

        if audited_final_sha != current_final_sha:
            logger.warning(
                f"[{lesson_id}] Audit report bound to different final SHA (report: {audited_final_sha}, disk: {current_final_sha}). Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "AUDIT_BINDING_MISMATCH")
            return False

        # 6. Authoritative audit invocation receipt provenance verification
        evidence_class = chk.get("evidence_class")
        if evidence_class not in ("REAL_AGY_VERIFIED", EVIDENCE_CLASS):
            logger.warning(
                f"[{lesson_id}] PASS checkpoint lacks verified evidence class (found: {evidence_class}). Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "UNVERIFIED_EVIDENCE_CLASS")
            return False

        inv_id = chk.get("audit_invocation_id")
        if not inv_id or not str(inv_id).strip():
            logger.warning(f"[{lesson_id}] PASS checkpoint lacks audit_invocation_id. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_MISSING")
            return False

        receipt = self.get_audit_receipt(str(inv_id).strip())
        if not receipt:
            logger.warning(f"[{lesson_id}] Audit invocation receipt missing for '{inv_id}'. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_MISSING")
            return False

        if receipt.get("lesson_id") != lesson_id:
            logger.warning(f"[{lesson_id}] Receipt lesson_id mismatch ({receipt.get('lesson_id')}). Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_LESSON_MISMATCH")
            return False

        if receipt.get("role") != "auditor":
            logger.warning(f"[{lesson_id}] Receipt role is not auditor ({receipt.get('role')}). Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_ROLE_MISMATCH")
            return False

        exec_mode = receipt.get("execution_mode") or receipt.get("mode")
        if not ((exec_mode in ("automated_cli", "agy") and receipt.get("evidence_class") == "REAL_AGY_VERIFIED") or verified_api_receipt(receipt)):
            logger.warning(f"[{lesson_id}] Receipt execution mode/evidence class not eligible for PASS. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_EXECUTION_MODE_INELIGIBLE")
            return False

        if receipt.get("audited_final_sha256") != current_final_sha:
            logger.warning(f"[{lesson_id}] Receipt audited_final_sha256 mismatch. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_FINAL_SHA_MISMATCH")
            return False

        if receipt.get("audit_report_sha256") != current_audit_sha:
            logger.warning(f"[{lesson_id}] Receipt audit_report_sha256 mismatch. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_REPORT_SHA_MISMATCH")
            return False

        if receipt.get("prompt_config_hash") != self.prompt_config_hash:
            logger.warning(f"[{lesson_id}] Receipt prompt_config_hash mismatch. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_CONFIG_PROMPT_CHANGED")
            return False

        if receipt.get("terminal_status") not in ("SUCCESS", "COMPLETED", "DONE", "OK"):
            logger.warning(f"[{lesson_id}] Receipt terminal status not successful. Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_TERMINAL_STATUS_FAILED")
            return False

        if receipt.get("model_verified") != "VERIFIED":
            logger.warning(f"[{lesson_id}] Receipt model is not VERIFIED ({receipt.get('model_verified')}). Invalidating PASS.")
            self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_MODEL_NOT_VERIFIED")
            return False

        if receipt.get("lesson_type"):
            if verified_lesson_type and receipt["lesson_type"] != verified_lesson_type:
                logger.warning(
                    f"[{lesson_id}] Receipt lesson_type mismatch (receipt '{receipt.get('lesson_type')}', expected '{verified_lesson_type}'). Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_CONTEXT_MISMATCH")
                return False

        if receipt.get("source_status"):
            if verified_source_status and receipt["source_status"] != verified_source_status:
                logger.warning(
                    f"[{lesson_id}] Receipt source_status mismatch (receipt '{receipt.get('source_status')}', expected '{verified_source_status}'). Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "AUDIT_RECEIPT_CONTEXT_MISMATCH")
                return False

        # 7. Visual artifacts integrity, figure reconciliation, and hash verification
        with open(final_path, "r", encoding="utf-8") as f_fin:
            final_md_text = f_fin.read()

        # Check figure marker integrity
        marker_errors = check_figure_markers(final_md_text)
        if marker_errors:
            logger.warning(
                f"[{lesson_id}] Malformed figure markers in final output: {marker_errors}. Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "VISUAL_MARKER_MALFORMED")
            return False

        actual_markdown_figs = extract_figures_from_markdown(final_md_text)
        untracked_figs = [
            f for f in actual_markdown_figs
            if f.get("is_untracked") or str(f.get("figure_id", "")).startswith("UNTRACKED")
        ]
        if untracked_figs:
            logger.warning(
                f"[{lesson_id}] Untracked Mermaid figure(s) detected in final output: {[f.get('figure_id') for f in untracked_figs]}. Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "VISUAL_UNTRACKED_FIGURE")
            return False

        actual_fig_count = len(actual_markdown_figs)
        report_figs_audited = report_data.get("visual_figures_audited")
        reported_vm_sha = report_data.get("visual_manifest_sha256")
        saved_vm_sha = chk.get("visual_manifest_sha256")
        visual_manifest_path = chk.get("visual_manifest_path")

        # 7a. Reconcile figure count between audit report and markdown
        if report_figs_audited is not None and report_figs_audited != actual_fig_count:
            logger.warning(
                f"[{lesson_id}] Visual figures count mismatch: audit report declares {report_figs_audited}, "
                f"but markdown has {actual_fig_count}. Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "VISUAL_FIGURES_MISMATCH")
            return False

        # 7b. Check visual manifest hash consistency between report and checkpoint
        if reported_vm_sha and saved_vm_sha and reported_vm_sha != saved_vm_sha:
            logger.warning(
                f"[{lesson_id}] Visual manifest hash mismatch between report ({reported_vm_sha}) and checkpoint ({saved_vm_sha}). Invalidating PASS."
            )
            self._invalidate_pass(lesson_id, chk, "VISUAL_MANIFEST_HASH_MISMATCH")
            return False

        # 7c. Nonvisual vs visual lesson verification
        has_visual_evidence = bool(
            reported_vm_sha
            or saved_vm_sha
            or visual_manifest_path
            or (report_figs_audited is not None and report_figs_audited > 0)
            or actual_fig_count > 0
        )
        if not has_visual_evidence:
            # Nonvisual lesson (e.g. QUIZ/GLOSSARY)
            pass
        else:
            if actual_fig_count > 0 and (report_figs_audited is None or report_figs_audited == 0):
                logger.warning(f"[{lesson_id}] Markdown contains {actual_fig_count} figures but audit report declares {report_figs_audited}. Invalidating PASS.")
                self._invalidate_pass(lesson_id, chk, "VISUAL_FIGURES_MISMATCH")
                return False

            if (report_figs_audited is not None and report_figs_audited > 0) and not reported_vm_sha:
                logger.warning(f"[{lesson_id}] Visual manifest sha256 missing in report. Invalidating PASS.")
                self._invalidate_pass(lesson_id, chk, "VISUAL_MANIFEST_MISSING")
                return False

            expected_vm_sha = reported_vm_sha or saved_vm_sha
            if not expected_vm_sha:
                logger.warning(f"[{lesson_id}] Visual manifest sha256 missing in report or checkpoint. Invalidating PASS.")
                self._invalidate_pass(lesson_id, chk, "VISUAL_MANIFEST_MISSING")
                return False

            if not visual_manifest_path or not os.path.exists(visual_manifest_path):
                visual_manifest_path = self._resolve_visual_manifest_path(lesson_id, final_path)

            if not visual_manifest_path or not os.path.exists(visual_manifest_path):
                logger.warning(f"[{lesson_id}] Visual manifest file missing on disk: {visual_manifest_path}. Invalidating PASS.")
                self._invalidate_pass(lesson_id, chk, "VISUAL_MANIFEST_MISSING")
                return False

            current_vm_sha = calculate_file_sha256(visual_manifest_path)
            if current_vm_sha != expected_vm_sha or (reported_vm_sha and current_vm_sha != reported_vm_sha):
                logger.warning(
                    f"[{lesson_id}] Visual manifest hash mismatch (saved: {saved_vm_sha}, current: {current_vm_sha}, report: {reported_vm_sha}). Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "VISUAL_MANIFEST_HASH_MISMATCH")
                return False

            try:
                with open(visual_manifest_path, "r", encoding="utf-8") as vmf:
                    vm_data = json.load(vmf)
            except Exception as e:
                logger.warning(f"[{lesson_id}] Failed to load visual manifest: {e}. Invalidating PASS.")
                self._invalidate_pass(lesson_id, chk, "VISUAL_MANIFEST_PARSE_ERROR")
                return False

            figures = vm_data.get("figures", [])
            if actual_fig_count > 0 and len(figures) != actual_fig_count:
                logger.warning(
                    f"[{lesson_id}] Visual manifest figures count {len(figures)} != markdown figures count {actual_fig_count}. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "VISUAL_FIGURES_MISMATCH")
                return False
            if report_figs_audited is not None and len(figures) != report_figs_audited:
                logger.warning(
                    f"[{lesson_id}] Visual manifest figures count {len(figures)} != report figures count {report_figs_audited}. Invalidating PASS."
                )
                self._invalidate_pass(lesson_id, chk, "VISUAL_FIGURES_MISMATCH")
                return False

            is_valid, err_cat, err_msg = validate_figure_semantic_binding(
                markdown_content=final_md_text,
                manifest_data=vm_data,
                resolve_path_fn=lambda p: self._resolve_asset_path(p, final_path),
            )
            if not is_valid:
                logger.warning(f"[{lesson_id}] {err_cat}: {err_msg}. Invalidating PASS.")
                self._invalidate_pass(lesson_id, chk, err_cat or "VISUAL_BINDING_MISMATCH")
                return False

        return True

    def _is_resumable_human_acceptance(
        self, lesson_id: str, chk: Dict[str, Any], current_source_sha256: str
    ) -> bool:
        """Validates that a HUMAN_ACCEPTED checkpoint has all valid hashes and intact artifacts."""
        if chk.get("evidence_class") != "HUMAN_ACCEPTED":
            logger.warning(f"[{lesson_id}] HUMAN_ACCEPTED checkpoint lacks valid evidence_class.")
            self._invalidate_human_acceptance(lesson_id, chk, "EVIDENCE_CLASS_NOT_HUMAN_ACCEPTED")
            return False

        # 1. Source hash check
        saved_source_sha = chk.get("source_sha256")
        if not saved_source_sha or saved_source_sha != current_source_sha256:
            logger.warning(f"[{lesson_id}] Source SHA256 mismatch in HUMAN_ACCEPTED checkpoint.")
            self._invalidate_human_acceptance(lesson_id, chk, "SOURCE_MISMATCH")
            return False

        # 2. Config & prompt hash check
        saved_prompt_cfg = chk.get("prompt_config_hash")
        if not saved_prompt_cfg or saved_prompt_cfg != self.prompt_config_hash:
            logger.warning(f"[{lesson_id}] Config/prompts changed for HUMAN_ACCEPTED checkpoint.")
            self._invalidate_human_acceptance(lesson_id, chk, "CONFIG_PROMPT_CHANGED")
            return False

        # 3. Final path and final sha256 check
        final_path = chk.get("final_path")
        if not final_path or not os.path.exists(final_path):
            logger.warning(f"[{lesson_id}] Final output file missing on disk: {final_path}.")
            self._invalidate_human_acceptance(lesson_id, chk, "FINAL_OUTPUT_MISSING")
            return False

        saved_final_sha = chk.get("final_sha256")
        current_final_sha = calculate_file_sha256(final_path)
        if not saved_final_sha or current_final_sha != saved_final_sha:
            logger.warning(f"[{lesson_id}] Final output modified for HUMAN_ACCEPTED lesson.")
            self._invalidate_human_acceptance(lesson_id, chk, "FINAL_OUTPUT_MODIFIED")
            return False

        # 4. Acceptance artifact file and sha256 check
        acceptance_path = chk.get("acceptance_path")
        saved_acceptance_sha = chk.get("acceptance_sha256")
        if not acceptance_path or not os.path.exists(acceptance_path):
            logger.warning(f"[{lesson_id}] Acceptance artifact missing on disk: {acceptance_path}.")
            self._invalidate_human_acceptance(lesson_id, chk, "ACCEPTANCE_ARTIFACT_MISSING")
            return False

        current_acceptance_sha = calculate_file_sha256(acceptance_path)
        if not saved_acceptance_sha or current_acceptance_sha != saved_acceptance_sha:
            logger.warning(f"[{lesson_id}] Acceptance artifact modified on disk.")
            self._invalidate_human_acceptance(lesson_id, chk, "ACCEPTANCE_ARTIFACT_MODIFIED")
            return False

        # 5. Parse acceptance artifact JSON and check bindings
        try:
            with open(acceptance_path, "r", encoding="utf-8") as af:
                artifact_data = json.load(af)
        except Exception as e:
            logger.warning(f"[{lesson_id}] Acceptance artifact invalid JSON: {e}.")
            self._invalidate_human_acceptance(lesson_id, chk, "ACCEPTANCE_ARTIFACT_PARSE_ERROR")
            return False

        if artifact_data.get("decision") != "APPROVED":
            logger.warning(f"[{lesson_id}] Acceptance artifact decision is not APPROVED.")
            self._invalidate_human_acceptance(lesson_id, chk, "ACCEPTANCE_DECISION_NOT_APPROVED")
            return False

        if artifact_data.get("lesson_id") != lesson_id:
            logger.warning(f"[{lesson_id}] Acceptance artifact lesson_id mismatch.")
            self._invalidate_human_acceptance(lesson_id, chk, "ACCEPTANCE_LESSON_ID_MISMATCH")
            return False

        if artifact_data.get("approved_final_sha256") != current_final_sha:
            logger.warning(f"[{lesson_id}] Acceptance artifact approved_final_sha256 mismatch.")
            self._invalidate_human_acceptance(lesson_id, chk, "ACCEPTANCE_FINAL_SHA256_MISMATCH")
            return False

        return True

    def _invalidate_pass(self, lesson_id: str, chk: Dict[str, Any], reason: str) -> None:
        """Transitions a stale, unverified, or tampered PASS checkpoint to INVALIDATED."""
        old_status = chk.get("status", "PASS")
        chk["status"] = "INVALIDATED"
        chk["error_category"] = f"INVALIDATED_{reason}"
        if "history" not in chk:
            chk["history"] = []
        chk["history"].append({
            "from_status": old_status,
            "to_status": "INVALIDATED",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "details": {"invalidation_reason": reason},
        })
        self.save_checkpoint(lesson_id, chk)

    def _invalidate_human_acceptance(self, lesson_id: str, chk: Dict[str, Any], reason: str) -> None:
        """Transitions a stale, unverified, or tampered HUMAN_ACCEPTED checkpoint to INVALIDATED."""
        old_status = chk.get("status", "HUMAN_ACCEPTED")
        chk["status"] = "INVALIDATED"
        chk["error_category"] = f"INVALIDATED_{reason}"
        if "history" not in chk:
            chk["history"] = []
        chk["history"].append({
            "from_status": old_status,
            "to_status": "INVALIDATED",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "details": {"invalidation_reason": reason},
        })
        self.save_checkpoint(lesson_id, chk)

    def record_human_approval(
        self,
        lesson_id: str,
        reviewer: str,
        approved_final_sha256: str,
        notes: Any = "",
        source: str = "HUMAN_OPERATOR",
    ) -> Dict[str, Any]:
        """Binds explicit human approval to a lesson's exact final content SHA256.
        Creates a durable acceptance artifact and transitions status to HUMAN_ACCEPTED.
        Fails closed if reviewer is missing, or approved SHA256 does not match disk file.
        Idempotent: if already approved with matching hash and intact artifact, returns checkpoint unchanged.
        """
        if not reviewer or not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError(f"Reviewer identifier is required for human approval on {lesson_id}")

        chk = self.load_checkpoint(lesson_id)
        if not chk:
            raise ValueError(f"No checkpoint found for lesson '{lesson_id}'")

        final_path = chk.get("final_path")
        if not final_path or not os.path.exists(final_path):
            raise FileNotFoundError(f"Final output file for {lesson_id} does not exist: {final_path}")

        current_final_sha = calculate_file_sha256(final_path)
        if current_final_sha != approved_final_sha256:
            raise ValueError(
                f"SHA256 mismatch for human approval on {lesson_id}: "
                f"approved '{approved_final_sha256}', disk file has '{current_final_sha}'"
            )

        # Idempotency check: if already approved with matching hash and intact acceptance artifact
        if chk.get("status") == "HUMAN_ACCEPTED" and chk.get("final_sha256") == approved_final_sha256:
            acc_path = chk.get("acceptance_path")
            acc_sha = chk.get("acceptance_sha256")
            if acc_path and os.path.exists(acc_path) and acc_sha:
                if calculate_file_sha256(acc_path) == acc_sha:
                    try:
                        with open(acc_path, "r", encoding="utf-8") as af:
                            art_data = json.load(af)
                        if (
                            art_data.get("decision") == "APPROVED"
                            and art_data.get("lesson_id") == lesson_id
                            and art_data.get("approved_final_sha256") == approved_final_sha256
                        ):
                            logger.info(f"[{lesson_id}] Human approval already recorded and intact (idempotent).")
                            return chk
                    except Exception:
                        pass

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        artifact_filename = f"{lesson_id}_acceptance.json"
        artifact_path = os.path.join(self.acceptance_dir, artifact_filename)
        artifact_data = {
            "lesson_id": lesson_id,
            "approved_final_sha256": approved_final_sha256,
            "reviewer": reviewer.strip(),
            "decision": "APPROVED",
            "timestamp": now,
            "source": source,
            "notes": notes,
            "identity_verification": "UNVERIFIED_CALLER_PROVIDED_IDENTITY",
        }
        with open(artifact_path, "w", encoding="utf-8") as af:
            json.dump(artifact_data, af, indent=2, ensure_ascii=False)

        artifact_sha256 = calculate_file_sha256(artifact_path)

        old_status = chk.get("status", "UNKNOWN")
        chk["status"] = "HUMAN_ACCEPTED"
        chk["verdict"] = "HUMAN_ACCEPTED"
        chk["evidence_class"] = "HUMAN_ACCEPTED"
        chk["final_sha256"] = approved_final_sha256
        chk["acceptance_path"] = artifact_path
        chk["acceptance_sha256"] = artifact_sha256
        chk["error_category"] = None
        chk["human_approval"] = {
            "reviewer": reviewer.strip(),
            "decision": "APPROVED",
            "evidence_class": "HUMAN_ACCEPTED",
            "approved_final_sha256": approved_final_sha256,
            "timestamp": now,
            "source": source,
            "artifact_path": artifact_path,
            "artifact_sha256": artifact_sha256,
            "notes": notes,
            "identity_verification": "UNVERIFIED_CALLER_PROVIDED_IDENTITY",
        }

        if "history" not in chk:
            chk["history"] = []
        chk["history"].append({
            "from_status": old_status,
            "to_status": "HUMAN_ACCEPTED",
            "timestamp": now,
            "details": {
                "action": "HUMAN_ACCEPTANCE_RECORDED",
                "reviewer": reviewer.strip(),
                "approved_final_sha256": approved_final_sha256,
                "artifact_path": artifact_path,
                "artifact_sha256": artifact_sha256,
                "notes": notes,
            },
        })
        self.save_checkpoint(lesson_id, chk)
        return chk

    def record_audit_verdict(
        self,
        lesson_id: str,
        verdict: Optional[str] = None,
        audit_path: Optional[str] = None,
        expected_final_sha256: Optional[str] = None,
        notes: str = "",
        validator: Optional[Any] = None,
        audit_invocation_id: Optional[str] = None,
        model_verified: Optional[str] = None,
        require_model_verification: bool = True,
        final_path: Optional[str] = None,
        visual_manifest_path: Optional[str] = None,
        visual_manifest_sha256: Optional[str] = None,
        visual_figures: Optional[List[Dict[str, Any]]] = None,
        quality_rubric_version: Optional[str] = None,
        lesson_type: Optional[str] = None,
        source_status: Optional[str] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        """Binds an independent audit verdict to the exact final content SHA256.
        The audit report file itself is authoritative; caller verdict is validated against report.
        Validates schema, lesson ID, verdict, absence of blocking findings/failed dimensions,
        and explicit binding to the audited final SHA-256 and Controller invocation receipt.
        """
        if not require_model_verification:
            raise ValueError(
                f"Cannot disable mandatory model verification for production audit verdict on {lesson_id}"
            )

        # Handle positional swap if caller passes audit_path as 2nd arg
        if audit_path is None and verdict and (verdict.endswith(".json") or os.path.exists(verdict)):
            audit_path = verdict
            verdict = None

        chk = self.load_checkpoint(lesson_id)
        if not chk:
            raise ValueError(f"No checkpoint found for lesson '{lesson_id}'")

        target_final_path = final_path or chk.get("final_path")
        if not target_final_path or not os.path.exists(target_final_path):
            raise FileNotFoundError(f"Final output file for {lesson_id} does not exist: {target_final_path}")

        current_final_sha = calculate_file_sha256(target_final_path)
        if expected_final_sha256 and current_final_sha != expected_final_sha256:
            raise ValueError(
                f"Audit verdict binding rejected: final SHA256 mismatch "
                f"(expected '{expected_final_sha256}', current '{current_final_sha}')"
            )

        if not audit_path or not os.path.exists(audit_path):
            raise FileNotFoundError(f"Audit report file not found: {audit_path}")

        audit_sha256 = calculate_file_sha256(audit_path)

        with open(target_final_path, "r", encoding="utf-8") as f_fin:
            final_md_text = f_fin.read()
        actual_markdown_figs = extract_figures_from_markdown(final_md_text)
        actual_fig_count = len(actual_markdown_figs)

        with open(audit_path, "r", encoding="utf-8") as af:
            raw_report_text = af.read()

        try:
            report_json = json.loads(raw_report_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Audit report file contains invalid JSON: {e}") from e

        # Context resolution and verification across caller, manifest, and checkpoint
        m_meta = self._get_manifest_lesson_meta(lesson_id)
        if m_meta:
            m_type = m_meta.get("source_type")
            m_status = m_meta.get("status")
            if lesson_type and lesson_type != m_type:
                raise ValueError(
                    f"Untrusted lesson context: caller passed lesson_type='{lesson_type}', "
                    f"but manifest defines '{m_type}' for {lesson_id}"
                )
            if source_status and source_status != m_status:
                raise ValueError(
                    f"Untrusted lesson context: caller passed source_status='{source_status}', "
                    f"but manifest defines '{m_status}' for {lesson_id}"
                )
            if chk.get("lesson_type") and chk.get("lesson_type") != m_type:
                raise ValueError(
                    f"Untrusted lesson context: checkpoint lesson_type '{chk.get('lesson_type')}' "
                    f"does not match manifest '{m_type}' for {lesson_id}"
                )
            if chk.get("source_status") and chk.get("source_status") != m_status:
                raise ValueError(
                    f"Untrusted lesson context: checkpoint source_status '{chk.get('source_status')}' "
                    f"does not match manifest '{m_status}' for {lesson_id}"
                )
            effective_lesson_type = m_type
            effective_source_status = m_status
        else:
            if lesson_type and chk.get("lesson_type") and lesson_type != chk.get("lesson_type"):
                raise ValueError(
                    f"Lesson context mismatch: caller lesson_type '{lesson_type}' "
                    f"does not match checkpoint '{chk.get('lesson_type')}'"
                )
            if source_status and chk.get("source_status") and source_status != chk.get("source_status"):
                raise ValueError(
                    f"Lesson context mismatch: caller source_status '{source_status}' "
                    f"does not match checkpoint '{chk.get('source_status')}'"
                )
            effective_lesson_type = lesson_type or chk.get("lesson_type")
            effective_source_status = source_status or chk.get("source_status")

        # Exemption context check: authoritative manifest is mandatory for visual exemptions
        report_dims = report_json.get("dimension_scores") or {}
        if report_dims.get("VISUAL_PEDAGOGY") == "NOT_APPLICABLE":
            if not m_meta:
                raise ValueError(
                    f"Untrusted exemption context: visual exemption for {lesson_id} "
                    f"requires an authoritative manifest"
                )
            if m_meta.get("source_type") not in ("QUIZ", "GLOSSARY") or m_meta.get("status") != "AVAILABLE":
                raise ValueError(
                    f"Unauthorized visual exemption: lesson {lesson_id} is '{m_meta.get('source_type')}' "
                    f"(status '{m_meta.get('status')}'), visual exemption only permitted for AVAILABLE QUIZ/GLOSSARY"
                )

        # Validate with AuditValidator
        if validator is not None:
            val = validator
        else:
            from course_harness.validator import AuditValidator
            val = AuditValidator(self.schema_path)

        # Validate report against schema and verdict consistency rules
        report, _ = val.validate_report(
            raw_report_text,
            expected_lesson_id=lesson_id,
            lesson_type=effective_lesson_type,
            source_status=effective_source_status,
            final_markdown=final_md_text,
        )

        report_verdict = report.get("verdict")
        if verdict and verdict != report_verdict:
            raise ValueError(
                f"Audit verdict rejected: caller requested '{verdict}' but authoritative "
                f"report verdict is '{report_verdict}'"
            )

        # Verify no blocking findings or FAILED dimensions
        findings = report.get("findings", [])
        blocking = [f for f in findings if f.get("severity") in ("HIGH", "BLOCKING")]
        if report_verdict == "PASS" and blocking:
            raise ValueError(f"Cannot grant PASS: report contains {len(blocking)} HIGH/BLOCKING finding(s)")

        dim_scores = report.get("dimension_scores", {})
        failed_dims = [dim for dim, score in dim_scores.items() if score == "FAILED"]
        if report_verdict == "PASS" and failed_dims:
            raise ValueError(f"Cannot grant PASS: report contains FAILED dimension(s): {failed_dims}")

        # Audited-final binding check
        audited_final_sha = report.get("audited_final_sha256")
        if not audited_final_sha or not isinstance(audited_final_sha, str) or not audited_final_sha.strip():
            raise ValueError(
                f"Audit verdict binding rejected: report for {lesson_id} lacks 'audited_final_sha256' binding"
            )

        if audited_final_sha != current_final_sha:
            raise ValueError(
                f"Audit verdict binding rejected: report audited_final_sha256 '{audited_final_sha}' "
                f"does not match disk final SHA256 '{current_final_sha}'"
            )

        target_status = "PASS" if report_verdict == "PASS" else ("NEEDS_HUMAN_REVIEW" if report_verdict == "FAIL" else "NEEDS_REAUDIT")

        # Invocations evidence and receipt verification
        inv_id = report.get("audit_invocation_id") or audit_invocation_id or chk.get("audit_invocation_id")
        if not inv_id or not str(inv_id).strip():
            raise ValueError(f"Missing actual invocation evidence for AI audit on {lesson_id}")
        inv_id = str(inv_id).strip()

        # Authoritative receipt and quality verification for production PASS
        if target_status == "PASS":
            receipt = self.get_audit_receipt(inv_id)
            if not receipt:
                raise ValueError(
                    f"Audit receipt provenance rejected: no controller audit receipt found for invocation '{inv_id}'"
                )

            # Context cross-check with receipt
            if receipt.get("lesson_type"):
                rcpt_type = receipt["lesson_type"]
                if effective_lesson_type and rcpt_type != effective_lesson_type:
                    raise ValueError(
                        f"Audit receipt provenance rejected: receipt lesson_type '{rcpt_type}' "
                        f"does not match effective lesson_type '{effective_lesson_type}'"
                    )
                if m_meta and rcpt_type != m_meta.get("source_type"):
                    raise ValueError(
                        f"Audit receipt provenance rejected: receipt lesson_type '{rcpt_type}' "
                        f"does not match manifest '{m_meta.get('source_type')}'"
                    )
                if chk.get("lesson_type") and rcpt_type != chk.get("lesson_type"):
                    raise ValueError(
                        f"Audit receipt provenance rejected: receipt lesson_type '{rcpt_type}' "
                        f"does not match checkpoint '{chk.get('lesson_type')}'"
                    )
                effective_lesson_type = effective_lesson_type or rcpt_type

            if receipt.get("source_status"):
                rcpt_status = receipt["source_status"]
                if effective_source_status and rcpt_status != effective_source_status:
                    raise ValueError(
                        f"Audit receipt provenance rejected: receipt source_status '{rcpt_status}' "
                        f"does not match effective source_status '{effective_source_status}'"
                    )
                if m_meta and rcpt_status != m_meta.get("status"):
                    raise ValueError(
                        f"Audit receipt provenance rejected: receipt source_status '{rcpt_status}' "
                        f"does not match manifest '{m_meta.get('status')}'"
                    )
                if chk.get("source_status") and rcpt_status != chk.get("source_status"):
                    raise ValueError(
                        f"Audit receipt provenance rejected: receipt source_status '{rcpt_status}' "
                        f"does not match checkpoint '{chk.get('source_status')}'"
                    )
                if source_status and rcpt_status != source_status:
                    raise ValueError(
                        f"Audit receipt provenance rejected: receipt source_status '{rcpt_status}' "
                        f"does not match caller source_status '{source_status}'"
                    )
                effective_source_status = effective_source_status or rcpt_status

            # Visual marker and untracked figure check
            marker_errors = check_figure_markers(final_md_text)
            if marker_errors:
                raise ValueError(f"VISUAL_MARKER_MALFORMED: {'; '.join(marker_errors)}")

            untracked_figs = [
                f for f in actual_markdown_figs
                if f.get("is_untracked") or str(f.get("figure_id", "")).startswith("UNTRACKED")
            ]
            if untracked_figs:
                raise ValueError(
                    f"VISUAL_UNTRACKED_FIGURE: Untracked visual figure(s) detected in Markdown: {[f.get('figure_id') for f in untracked_figs]}"
                )

            # Visual evidence reconciliation and verification
            report_figs = report.get("visual_figures_audited")
            report_vm_sha = report.get("visual_manifest_sha256")
            chk_vm_sha = chk.get("visual_manifest_sha256")

            if chk_vm_sha and report_vm_sha and chk_vm_sha != report_vm_sha:
                raise ValueError(
                    f"Visual manifest hash mismatch between audit report ('{report_vm_sha}') "
                    f"and checkpoint ('{chk_vm_sha}')"
                )

            has_visual_evidence = bool(
                report_vm_sha
                or visual_manifest_sha256
                or visual_manifest_path
                or (report_figs is not None and report_figs > 0)
                or actual_fig_count > 0
            )

            if not has_visual_evidence:
                # Legitimate nonvisual QUIZ/GLOSSARY
                verified_vm_path = None
                verified_vm_sha = None
                verified_figures = []
            else:
                if report_figs is not None and report_figs != actual_fig_count:
                    raise ValueError(
                        f"Figure count mismatch: audit report declares visual_figures_audited={report_figs}, "
                        f"but markdown contains {actual_fig_count} figure(s)"
                    )
                if actual_fig_count > 0 and (report_figs is None or report_figs == 0):
                    raise ValueError(
                        f"Markdown contains {actual_fig_count} figure(s) but audit report declares visual_figures_audited={report_figs}"
                    )
                if (report_figs is not None and report_figs > 0) and not report_vm_sha:
                    raise ValueError(
                        f"Audit report claims {report_figs} visual figure(s) but lacks visual_manifest_sha256"
                    )
                if report_vm_sha and visual_manifest_sha256 and visual_manifest_sha256 != report_vm_sha:
                    raise ValueError(
                        f"Visual manifest SHA256 mismatch between caller ('{visual_manifest_sha256}') "
                        f"and audit report ('{report_vm_sha}')"
                    )

                expected_vm_sha = report_vm_sha or visual_manifest_sha256 or chk_vm_sha
                vm_path = visual_manifest_path or report.get("visual_manifest_path") or chk.get("visual_manifest_path")
                if not vm_path or not os.path.exists(vm_path):
                    vm_path = self._resolve_visual_manifest_path(lesson_id, target_final_path)

                if not vm_path or not os.path.exists(vm_path):
                    raise ValueError(
                        f"Production PASS rejected: visual manifest file missing on disk for {lesson_id}"
                    )

                current_vm_sha = calculate_file_sha256(vm_path)
                if expected_vm_sha and current_vm_sha != expected_vm_sha:
                    raise ValueError(
                        f"Visual manifest SHA256 mismatch: disk file '{current_vm_sha}' != expected '{expected_vm_sha}'"
                    )

                try:
                    with open(vm_path, "r", encoding="utf-8") as vmf:
                        vm_data = json.load(vmf)
                except Exception as e:
                    raise ValueError(f"Failed to parse visual manifest for {lesson_id}: {e}")

                manifest_figures = vm_data.get("figures", [])
                if actual_fig_count > 0 and len(manifest_figures) != actual_fig_count:
                    raise ValueError(
                        f"Figure count mismatch: visual manifest figure count {len(manifest_figures)} != markdown figure count {actual_fig_count}"
                    )
                if report_figs is not None and len(manifest_figures) != report_figs:
                    raise ValueError(
                        f"Figure count mismatch: visual manifest figure count {len(manifest_figures)} != audit report figures {report_figs}"
                    )

                is_valid, err_cat, err_msg = validate_figure_semantic_binding(
                    markdown_content=final_md_text,
                    manifest_data=vm_data,
                    resolve_path_fn=lambda p: self._resolve_asset_path(p, target_final_path),
                )
                if not is_valid:
                    raise ValueError(f"{err_cat}: {err_msg}")

                verified_vm_path = vm_path
                verified_vm_sha = expected_vm_sha or current_vm_sha
                verified_figures = manifest_figures

            # 0. Quality eligibility check at the StateManager boundary!
            from course_harness.validator import is_production_quality_eligible
            q_eligible, q_reason = is_production_quality_eligible(
                report,
                lesson_type=effective_lesson_type,
                source_status=effective_source_status,
            )
            if not q_eligible:
                raise ValueError(
                    f"Production PASS rejected: report fails current educational quality eligibility: {q_reason}"
                )

            # 1. Lesson ID check
            if receipt.get("lesson_id") != lesson_id:
                raise ValueError(
                    f"Audit receipt rejected: lesson ID mismatch (receipt '{receipt.get('lesson_id')}', expected '{lesson_id}')"
                )

            # 2. Invocation role check
            if receipt.get("role") != "auditor":
                raise ValueError(
                    f"Audit receipt rejected: invocation role is '{receipt.get('role')}', expected 'auditor'"
                )

            # 3. Execution mode check (eligible real AGY invocation, never mock)
            exec_mode = receipt.get("execution_mode") or receipt.get("mode")
            ev_class = receipt.get("evidence_class")
            if exec_mode == "mock" or ev_class == "MOCK_SIMULATED":
                raise ValueError(
                    "Audit receipt rejected: mock execution receipt cannot grant production PASS"
                )
            if exec_mode not in ("automated_cli", "agy", "gemini_api"):
                raise ValueError(
                    f"Audit receipt rejected: execution mode '{exec_mode}' is not eligible for production PASS"
                )
            if not ((exec_mode in ("automated_cli", "agy") and ev_class == "REAL_AGY_VERIFIED") or verified_api_receipt(receipt)):
                raise ValueError(
                    f"Audit receipt rejected: evidence class is '{ev_class}', expected 'REAL_AGY_VERIFIED'"
                )

            # 4. Final SHA binding check
            receipt_final_sha = receipt.get("audited_final_sha256")
            if not receipt_final_sha or receipt_final_sha != current_final_sha:
                raise ValueError(
                    f"Audit receipt rejected: receipt audited_final_sha256 '{receipt_final_sha}' "
                    f"does not match final SHA256 '{current_final_sha}'"
                )

            # 5. Source hash binding check
            chk_src = chk.get("source_sha256")
            receipt_src = receipt.get("source_sha256")
            if not receipt_src or (chk_src and receipt_src != chk_src):
                raise ValueError(
                    f"Audit receipt rejected: source_sha256 mismatch "
                    f"(receipt '{receipt_src}', checkpoint '{chk_src}')"
                )

            # 6. Prompt / config hash check
            receipt_cfg = receipt.get("prompt_config_hash")
            if not receipt_cfg or receipt_cfg != self.prompt_config_hash:
                raise ValueError(
                    f"Audit receipt rejected: prompt_config_hash mismatch "
                    f"(receipt '{receipt_cfg}', expected '{self.prompt_config_hash}')"
                )

            # 7. Provider terminal status check
            term_status = receipt.get("terminal_status")
            if term_status not in ("SUCCESS", "COMPLETED", "DONE", "OK"):
                raise ValueError(
                    f"Audit receipt rejected: provider terminal status '{term_status}' is not successful"
                )

            # 8. Model requested, reported, and verified check
            model_req = receipt.get("model_requested")
            model_rep = receipt.get("model_reported")
            receipt_mv = receipt.get("model_verified")
            if not verified_api_receipt(receipt) and (model_req != "gemini-3.8-flash-high" or model_rep != "gemini-3.8-flash-high"):
                raise ValueError(
                    f"Audit receipt rejected: model reported '{model_rep}' does not match required model 'gemini-3.8-flash-high'"
                )
            if receipt_mv != "VERIFIED":
                raise ValueError(
                    f"Audit receipt rejected: receipt lacks required model verification ('{receipt_mv}')"
                )

            # 9. Link between audit report and receipt
            report_inv = report.get("audit_invocation_id")
            if report_inv and report_inv != inv_id:
                raise ValueError(
                    f"Audit receipt rejected: invocation ID mismatch between report ('{report_inv}') and receipt ('{inv_id}')"
                )

            # 10. Audit artifact checksum match
            receipt_audit_sha = receipt.get("audit_report_sha256")
            if not receipt_audit_sha or receipt_audit_sha != audit_sha256:
                raise ValueError(
                    f"Audit receipt rejected: audit report checksum mismatch "
                    f"(receipt '{receipt_audit_sha}', disk '{audit_sha256}')"
                )

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        old_status = chk.get("status", "UNKNOWN")
        chk["final_path"] = target_final_path
        chk["audit_path"] = audit_path
        chk["audit_sha256"] = audit_sha256
        chk["final_sha256"] = current_final_sha
        chk["verdict"] = report_verdict
        chk["status"] = target_status
        chk["audit_invocation_id"] = inv_id
        if target_status == "PASS":
            chk["evidence_class"] = receipt["evidence_class"]
            chk["audit_receipt_path"] = os.path.join(self.receipts_dir, f"{inv_id}.json")
            chk["model_verified"] = "VERIFIED"
            chk["error_category"] = None
        else:
            chk["error_category"] = f"AUDIT_{report_verdict}"
            if model_verified or report.get("model_verification"):
                chk["model_verified"] = report.get("model_verification") or model_verified

        # Bind visual artifacts & rubric metadata if provided or in report
        if target_status == "PASS":
            if verified_vm_path:
                chk["visual_manifest_path"] = verified_vm_path
            if verified_vm_sha:
                chk["visual_manifest_sha256"] = verified_vm_sha
            if verified_figures is not None:
                chk["visual_figures"] = verified_figures
                chk["visual_figures_audited"] = len(verified_figures)
        else:
            vm_p = visual_manifest_path or report.get("visual_manifest_path")
            vm_s = visual_manifest_sha256 or report.get("visual_manifest_sha256")
            vf = visual_figures or report.get("visual_figures")
            if vm_p:
                chk["visual_manifest_path"] = vm_p
            if vm_s:
                chk["visual_manifest_sha256"] = vm_s
            if vf:
                chk["visual_figures"] = vf

        qrv = quality_rubric_version or report.get("quality_rubric_version")
        qs = report.get("quality_score")
        if qrv:
            chk["quality_rubric_version"] = qrv
        if qs is not None:
            chk["quality_score"] = qs
        cqa = report.get("content_quality_accepted")
        if cqa is not None:
            chk["content_quality_accepted"] = cqa

        if effective_lesson_type:
            chk["lesson_type"] = effective_lesson_type
        if effective_source_status:
            chk["source_status"] = effective_source_status

        if "history" not in chk:
            chk["history"] = []
        chk["history"].append({
            "from_status": old_status,
            "to_status": target_status,
            "timestamp": now,
            "details": {
                "action": "AUDIT_VERDICT_BOUND",
                "verdict": report_verdict,
                "audit_path": audit_path,
                "audit_sha256": audit_sha256,
                "final_sha256": current_final_sha,
                "audit_invocation_id": inv_id,
                "notes": notes,
            },
        })
        if persist:
            self.save_checkpoint(lesson_id, chk)
        return chk
