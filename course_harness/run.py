#!/usr/bin/env python3
"""Course Harness Controller (CLI Runner).

Orchestrates the multi-agent course production pipeline:
Worker (drafting) -> Auditor (independent audit) -> Repair (targeted fix) -> Final lesson.
Supports automated_cli, manual_cli_handoff, and mock execution modes.
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

import yaml

from course_harness.cli_adapter import (
    AgyAdapter,
    CliExecutionError,
    ModelUnavailableError,
    redact_signed_urls,
)
from course_harness.gemini_adapter import (
    GeminiApiAdapter, GeminiApiError, ApiDisabledError, ApiIntegrityError, verified_api_receipt, sha256,
)
from course_harness.provider_policy import AGY_BATCH_BLOCK_REASON, provider_readiness
from course_harness.ingest import calculate_sha256, ingest_course
from course_harness.state import StateManager, compute_prompt_config_hash
from course_harness.validator import (
    AuditValidator,
    ValidationError,
    classify_draft_issues,
    is_production_quality_eligible,
    validate_draft_structure,
)
from course_harness.visual import (
    VisualAssetManager,
    extract_figures_from_markdown,
    normalize_markdown_asset_paths,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("course_harness")

class ManifestStaleError(ApiIntegrityError):
    """Raised when on-disk source content hash diverges from manifest.json."""
    pass


class BlockedExecutionError(Exception):
    """Raised when bulk automated execution is attempted without proper authorization."""
    pass


PILOT_LESSON_IDS = ["M01-L07", "M02-L11", "M03-L08"]


class CourseHarnessController:
    """Main orchestrator for course curriculum production."""

    def __init__(self, config_path: str = "course_harness/config.yaml", mode_override: Optional[str] = None):
        self.config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.execution_mode = mode_override or self.config.get("execution", {}).get("mode", "automated_cli")
        if self.execution_mode == "gemini_api" and self.config.get("execution", {}).get("enabled") is False:
            raise ApiDisabledError("GEMINI_API_NOT_AUTHORIZED: Archived provider configuration is inactive")
        self.max_repair_rounds = min(2, max(0, self.config.get("workflow", {}).get("max_repair_rounds", 2)))

        paths = self.config.get("paths", {})
        self.course_id = paths.get("course_id", "Agile_Project_Management")
        self.source_dir = paths.get("source_dir", "output_course/Agile_Project_Management")
        self.output_dir = paths.get("output_dir", "generated_course/Agile_Project_Management")
        self.prompts_dir = paths.get("prompts_dir", "course_harness/prompts")
        self.schema_path = paths.get("schema_path", "course_harness/schemas/audit.schema.json")
        self.manifest_path = paths.get("manifest_path", os.path.join(self.output_dir, "manifest.json"))

        # Setup directory paths
        self.drafts_dir = os.path.join(self.output_dir, "drafts")
        self.audits_dir = os.path.join(self.output_dir, "audits")
        self.evidence_dir = os.path.join(self.output_dir, "evidence")
        self.modules_dir = os.path.join(self.output_dir, "modules")
        self.checkpoints_dir = os.path.join(self.evidence_dir, "checkpoints")
        self.receipts_dir = os.path.join(self.evidence_dir, "receipts")
        self.assets_dir = os.path.join(self.output_dir, "assets")

        for d in [self.drafts_dir, self.audits_dir, self.evidence_dir, self.modules_dir, self.checkpoints_dir, self.receipts_dir, self.assets_dir]:
            os.makedirs(d, exist_ok=True)

        # Stage assets symlink in drafts directory so relative links resolve during review
        drafts_assets_link = os.path.join(self.drafts_dir, "assets")
        if not os.path.exists(drafts_assets_link):
            try:
                os.symlink(os.path.relpath(self.assets_dir, self.drafts_dir), drafts_assets_link)
            except Exception:
                pass

        # Stage assets symlink in existing module directories so relative links resolve from publication layout
        if os.path.exists(self.modules_dir):
            for m_name in os.listdir(self.modules_dir):
                m_path = os.path.join(self.modules_dir, m_name)
                if os.path.isdir(m_path):
                    m_assets_link = os.path.join(m_path, "assets")
                    if not os.path.exists(m_assets_link):
                        try:
                            os.symlink(os.path.relpath(self.assets_dir, m_path), m_assets_link)
                        except Exception:
                            pass

        self.visual_asset_mgr = VisualAssetManager(self.assets_dir, automatic=self.execution_mode == "gemini_api")
        self._last_lesson_visuals: Dict[str, Any] = {}

        # Initialize components
        self.prompt_config_hash = compute_prompt_config_hash(self.prompts_dir, self.config_path)
        self.state_mgr = StateManager(
            self.checkpoints_dir,
            self.prompt_config_hash,
            receipts_dir=self.receipts_dir,
            manifest_path=self.manifest_path,
        )
        self.validator = AuditValidator(self.schema_path)

        # Worker & Auditor use gemini-3.8-flash-high pinned
        worker_cfg = self.config.get("models", {}).get("worker", {})
        self.model_id = worker_cfg.get("model", "gemini-3.8-flash-high")
        self.effort = worker_cfg.get("effort", "high")

        if self.execution_mode == "gemini_api":
            self.model_id = "gemini-3.8-flash"
            self.effort = "high"
            for role in ("worker", "auditor", "repair"):
                cfg = self.config.get("models", {}).get(role, {})
                if cfg.get("model", self.model_id) != self.model_id or cfg.get("effort", "high") != "high":
                    raise ValueError("Gemini API requires gemini-3.8-flash and high thinking for every role")
            self.adapter = GeminiApiAdapter(
                evidence_dir=self.evidence_dir, schema_path=self.schema_path,
                timeout_seconds=self.config.get("execution", {}).get("timeout_seconds", 180),
                max_retries=self.config.get("execution", {}).get("max_retries", 2),
            )
        else:
            self.adapter = AgyAdapter(
                mode=self.execution_mode,
                agy_binary=self.config.get("execution", {}).get("agy_binary"),
                timeout_seconds=self.config.get("execution", {}).get("timeout_seconds", 180),
                model=self.model_id,
                effort=self.effort,
                evidence_dir=self.evidence_dir,
            )

        self.manifest: Optional[Dict[str, Any]] = None

    def verify_system(self) -> Dict[str, Any]:
        """Verifies environment, CLI binary, and model availability."""
        logger.info(f"Verifying environment (mode: {self.execution_mode}, model: {self.model_id})...")
        try:
            info = self.adapter.verify_environment()
            logger.info(f"Verification successful: {info}")
            return info
        except ModelUnavailableError as e:
            logger.error(f"Environment verification failed: {e}")
            raise

    def get_manifest(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Loads or builds the course manifest deterministically."""
        if self.manifest and not force_refresh:
            return self.manifest

        if os.path.exists(self.manifest_path) and not force_refresh:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                self.manifest = json.load(f)
                self._manifest_sha256 = calculate_sha256(self.manifest_path)
                if self.execution_mode == "gemini_api" and self.manifest.get("course_id") != self.course_id:
                    raise ApiIntegrityError("Manifest course ID does not match configured course")
                return self.manifest

        logger.info(f"Ingesting raw course sources from '{self.source_dir}'...")
        self.manifest = ingest_course(self.source_dir, self.manifest_path)
        logger.info(
            f"Ingestion complete: {self.manifest['total_modules']} modules, "
            f"{self.manifest['total_lessons']} lessons indexed."
        )
        return self.manifest

    def _load_prompt_template(self, role: str) -> str:
        p_path = os.path.join(self.prompts_dir, f"{role}.md")
        with open(p_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        if self.execution_mode == "gemini_api":
            prompt += "\nAUTOMATIC PRODUCTION POLICY: All lesson text must be Vietnamese. Use only conceptual Mermaid diagrams rendered locally. No instructor/author photos, portraits, avatars, headshots, video screenshots or recognizable likenesses. No external or embedded images. Use Vietnamese prose for source limitations; never fabricate missing Coursera data. Human visual review remains pending. Never claim HUMAN_ACCEPTED.\n"
        return prompt

    def process_lesson(self, lesson_id: str, reset: bool = False) -> Dict[str, Any]:
        """Processes a single lesson through the Worker -> Auditor -> Repair pipeline."""
        manifest = self.get_manifest()
        lesson_meta = manifest.get("lessons", {}).get(lesson_id)
        if not lesson_meta:
            raise KeyError(f"Lesson ID '{lesson_id}' not found in manifest")

        from course_harness.batch import APPROVED_BASELINES
        accepted = self.state_mgr.load_checkpoint(lesson_id)
        approved_dir = self.config.get("paths", {}).get("approved_output_dir")
        if approved_dir and not accepted:
            approved_checkpoint = os.path.join(approved_dir, "evidence", "checkpoints", lesson_id + ".json")
            if os.path.isfile(approved_checkpoint):
                with open(approved_checkpoint, encoding="utf-8") as af:
                    inherited = json.load(af)
                if inherited.get("status") == "HUMAN_ACCEPTED":
                    accepted = inherited
        if lesson_id in APPROVED_BASELINES or (accepted and accepted.get("status") == "HUMAN_ACCEPTED"):
            return accepted or {"lesson_id": lesson_id, "status": "SKIPPED", "skip_reason": "PROTECTED_BASELINE"}

        raw_rel_path = lesson_meta["relative_path"]
        raw_full_path = os.path.join(self.source_dir, raw_rel_path)
        if self.execution_mode == "gemini_api" and os.path.commonpath([os.path.realpath(self.source_dir), os.path.realpath(raw_full_path)]) != os.path.realpath(self.source_dir):
            raise ApiIntegrityError("Source path escapes configured source directory")
        if not os.path.exists(raw_full_path):
            raise FileNotFoundError(f"Raw source file missing on disk: {raw_full_path}")

        # Recompute source hash on disk immediately
        current_source_sha256 = calculate_sha256(raw_full_path)

        # Detect stale manifest
        if current_source_sha256 != lesson_meta.get("source_sha256"):
            raise ManifestStaleError(
                f"MANIFEST_STALE: Raw source file '{raw_rel_path}' on disk (sha: {current_source_sha256}) "
                f"does not match manifest sha ({lesson_meta.get('source_sha256')}). Re-run ingest."
            )

        with open(raw_full_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        if self.execution_mode == "gemini_api":
            return self._process_api_lesson(lesson_meta, raw_content, reset)

        source_type = lesson_meta["source_type"]
        status = lesson_meta["status"]

        # 1. Check if already passed and resumable
        if not reset and self.state_mgr.is_resumable_pass(
            lesson_id,
            current_source_sha256,
            lesson_type=source_type,
            source_status=status,
        ):
            logger.info(f"[{lesson_id}] Resumable PASS detected. Skipping model inference.")
            chk = self.state_mgr.load_checkpoint(lesson_id)
            return chk or {}

        # Reset state if requested
        if reset:
            chk_path = self.state_mgr._get_checkpoint_path(lesson_id)
            if os.path.exists(chk_path):
                os.remove(chk_path)

        state = self.state_mgr.initialize_lesson_state(
            lesson_id=lesson_id,
            source_sha256=current_source_sha256,
            model_id=self.model_id,
            effort=self.effort,
            execution_mode=self.execution_mode,
            lesson_type=source_type,
            source_status=status,
        )

        logger.info(f"[{lesson_id}] Processing: '{lesson_meta['title']}' ({source_type}, status: {status})")

        # Handle LOCKED or UNAVAILABLE content
        if status in ("LOCKED", "UNAVAILABLE"):
            logger.warning(f"[{lesson_id}] Content is {status}. Generating formal notice.")
            notice_content = (
                f"# {lesson_meta['title']} (SOURCE_UNAVAILABLE)\n\n"
                f"> **Mã bài học:** {lesson_id}  \n"
                f"> **Trạng thái gốc:** {status}  \n"
                f"> **Lưu ý:** Bài học này chưa được mở khóa trên nền tảng nguồn.\n\n"
                f"## Thông báo học liệu\n"
                f"Nội dung học liệu này yêu cầu hoàn thành các bài học tiên quyết trước khi có thể truy cập.\n"
            )
            final_path = os.path.join(
                self.modules_dir, lesson_meta["module_id"], f"{lesson_id}_LOCKED.md"
            )
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, "w", encoding="utf-8") as f:
                f.write(notice_content)

            return self.state_mgr.transition(
                lesson_id,
                "BLOCKED",
                {
                    "error_category": f"SOURCE_{status}",
                    "final_path": final_path,
                    "verdict": "INCONCLUSIVE",
                },
            )

        # Check if an existing valid draft can be safely reused (e.g. recovery / resume mode without reset)
        reused_draft = False
        current_chk = self.state_mgr.load_checkpoint(lesson_id)
        if (
            not reset
            and current_chk
            and current_chk.get("draft_path")
            and os.path.exists(current_chk.get("draft_path"))
        ):
            candidate_draft_path = current_chk["draft_path"]
            with open(candidate_draft_path, "r", encoding="utf-8") as df:
                candidate_draft_content = df.read()
            if candidate_draft_content.strip():
                logger.info(f"[{lesson_id}] Reusing existing draft from '{candidate_draft_path}' for audit recovery.")
                # Reconcile candidate draft asset paths with manifest if available
                manifest_file = os.path.join(self.assets_dir, lesson_id, "visual_manifest.json")
                if os.path.exists(manifest_file):
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as mf:
                            m_data = json.load(mf)
                        norm_content = normalize_markdown_asset_paths(candidate_draft_content, m_data, lesson_id=lesson_id)
                        if norm_content != candidate_draft_content:
                            candidate_draft_content = norm_content
                            with open(candidate_draft_path, "w", encoding="utf-8") as df:
                                df.write(candidate_draft_content)
                    except Exception as e:
                        logger.warning(f"[{lesson_id}] Could not normalize candidate draft assets: {e}")
                draft_content = candidate_draft_content
                draft_path = candidate_draft_path
                reused_draft = True
                # Load worker metadata from evidence receipt if available
                worker_ev_path = current_chk.get("worker_evidence_path") or os.path.join(
                    self.evidence_dir, f"evidence_worker_{lesson_id}_att1.json")
                if os.path.exists(worker_ev_path):
                    try:
                        with open(worker_ev_path, "r", encoding="utf-8") as wf:
                            worker_meta = json.load(wf)
                    except Exception:
                        worker_meta = {"role": "worker", "model_verified": "NOT_VERIFIED"}
                else:
                    worker_meta = {"role": "worker", "model_verified": "NOT_VERIFIED"}

                # If worker_meta exists from real AGY execution, resolve model verification from session if needed
                if worker_meta.get("model_verified") != "VERIFIED" and worker_meta.get("conversation_id"):
                    res_m, sess_ev = self.adapter.resolve_session_model(worker_meta["conversation_id"])
                    if res_m and res_m == self.model_id:
                        worker_meta["model_reported"] = res_m
                        worker_meta["model_verified"] = "VERIFIED"
                        worker_meta["evidence_class"] = "REAL_AGY_VERIFIED"
                        if sess_ev:
                            worker_meta["model_verification_evidence"] = sess_ev
                        try:
                            with open(worker_ev_path, "w", encoding="utf-8") as wf:
                                json.dump(worker_meta, wf, indent=2, ensure_ascii=False)
                        except Exception:
                            pass

                lesson_inferences = [worker_meta]
                if state.get("status") == "PENDING":
                    self.state_mgr.transition(
                        lesson_id,
                        "DRAFTED",
                        {
                            "draft_path": draft_path,
                            "draft_version": current_chk.get("draft_version", 1),
                            "evidence_class": worker_meta.get("evidence_class", "REAL_AGY_VERIFIED"),
                            "visual_manifest_sha256": None,
                        },
                    )

        if not reused_draft:
            # STEP 1: WORKER DRAFTING
            res_worker = self._run_worker_draft(lesson_meta, raw_content)
            lesson_inferences: List[Dict[str, Any]] = []
            if len(res_worker) == 3:
                draft_content, draft_path, worker_meta = res_worker
                lesson_inferences.append(worker_meta)
            else:
                draft_content, draft_path = res_worker
                worker_meta = {}

            if self.execution_mode == "mock":
                self.state_mgr.transition(
                    lesson_id,
                    "MOCK_DRAFTED",
                    {"draft_path": draft_path, "draft_version": 1, "evidence_class": "MOCK_SIMULATED"},
                )
            else:
                self.state_mgr.transition(
                    lesson_id,
                    "DRAFTED",
                    {"draft_path": draft_path, "draft_version": 1,
                     "worker_evidence_path": worker_meta.get("evidence_path"),
                     "evidence_class": worker_meta.get("evidence_class", "REAL_AGY_VERIFIED"), "visual_manifest_sha256": None},
                )

        # STEP 2 & 3: AUDIT & REPAIR LOOP
        current_draft = draft_content
        current_draft_path = draft_path
        repair_attempt = 0
        final_verdict = "INCONCLUSIVE"
        audit_report: Dict[str, Any] = {}
        audit_path: str = ""
        last_audit_meta: Dict[str, Any] = {}

        # Validate draft visual asset integrity and block advancement to Auditor if broken image paths remain
        draft_issues = validate_draft_structure(
            current_draft,
            lesson_meta["source_type"],
            lesson_id=lesson_id,
            raw_source_content=raw_content,
            base_dir=self.output_dir,
            check_student_cleanliness=False,
        )
        blocking_asset_issues = [
            i for i in draft_issues
            if "Broken relative image path" in i
            or "Dangerous path traversal" in i
            or "Prohibited external signed URL" in i
            or "PROHIBITED_INSTRUCTOR_IMAGE" in i
        ]
        if blocking_asset_issues:
            logger.error(
                f"[{lesson_id}] Blocking draft-integrity errors prevent advancement to Auditor: "
                f"{blocking_asset_issues}"
            )
            return self.state_mgr.transition(
                lesson_id,
                "NEEDS_HUMAN_REVIEW",
                {
                    "error_category": f"DRAFT_INTEGRITY_ERROR: {'; '.join(blocking_asset_issues)}",
                    "draft_path": current_draft_path,
                    "verdict": "INCONCLUSIVE",
                },
            )

        while repair_attempt <= self.max_repair_rounds:
            audit_attempt = repair_attempt + 1
            if self.execution_mode == "manual_cli_handoff":
                for a in range(self.max_repair_rounds + 1, 0, -1):
                    h_file = os.path.join(self.evidence_dir, f"handoff_auditor_{lesson_id}_att{a}.json")
                    o_file = os.path.join(self.evidence_dir, f"output_auditor_{lesson_id}_att{a}.txt")
                    if os.path.exists(h_file) or os.path.exists(o_file):
                        audit_attempt = max(audit_attempt, a)
                        break

            # Independent Auditor (fresh session)
            try:
                res_auditor = self._run_auditor(
                    lesson_meta, raw_content, current_draft, attempt=audit_attempt
                )
            except ValidationError as e:
                bad_audit_path = os.path.join(self.audits_dir, f"{lesson_id}_audit_v{audit_attempt}_INVALID.txt")
                logger.error(
                    f"[{lesson_id}] Auditor output failed validation ({e}). "
                    f"Preserving raw response at '{bad_audit_path}' and transitioning to NEEDS_HUMAN_REVIEW."
                )
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": f"AUDIT_VALIDATION_ERROR: {e}",
                        "draft_path": current_draft_path,
                        "audit_path": bad_audit_path,
                        "verdict": "INCONCLUSIVE",
                    },
                )

            if len(res_auditor) == 3:
                audit_report, audit_path, auditor_meta = res_auditor
                lesson_inferences.append(auditor_meta)
            else:
                audit_report, audit_path = res_auditor
                auditor_meta = {}
            last_audit_meta = auditor_meta
            final_verdict = audit_report.get("verdict", "INCONCLUSIVE")

            if self.execution_mode == "mock":
                self.state_mgr.transition(
                    lesson_id,
                    "MOCK_AUDITED",
                    {
                        "audit_path": audit_path,
                        "audit_version": audit_attempt,
                        "verdict": final_verdict,
                        "evidence_class": "MOCK_SIMULATED",
                    },
                )
            else:
                audit_transition_updates = {
                    "audit_path": audit_path,
                    "audit_version": audit_attempt,
                    "verdict": final_verdict,
                }
                if audit_report.get("visual_manifest_sha256"):
                    audit_transition_updates["visual_manifest_sha256"] = audit_report["visual_manifest_sha256"]
                self.state_mgr.transition(
                    lesson_id,
                    "AUDITED",
                    audit_transition_updates,
                )

            if final_verdict == "PASS":
                # Verify central production quality eligibility check!
                # Even if report says PASS, historical audit or failed hard gates cannot grant production PASS!
                q_eligible, q_reason = is_production_quality_eligible(
                    audit_report,
                    lesson_type=lesson_meta.get("source_type"),
                    source_status=lesson_meta.get("status"),
                )
                if not q_eligible:
                    logger.warning(
                        f"[{lesson_id}] Audit report verdict is PASS but production quality eligibility check failed: {q_reason}"
                    )
                    return self.state_mgr.transition(
                        lesson_id,
                        "NEEDS_HUMAN_REVIEW",
                        {
                            "error_category": f"QUALITY_ELIGIBILITY_FAILED: {q_reason}",
                            "draft_path": current_draft_path,
                            "audit_path": audit_path,
                        },
                    )

                logger.info(f"[{lesson_id}] Audit PASSED and quality eligible on attempt {audit_attempt}!")
                break

            if final_verdict == "FAIL":
                if repair_attempt >= self.max_repair_rounds:
                    logger.warning(
                        f"[{lesson_id}] Max repair rounds ({self.max_repair_rounds}) reached. "
                        f"Status -> NEEDS_HUMAN_REVIEW."
                    )
                    return self.state_mgr.transition(
                        lesson_id,
                        "NEEDS_HUMAN_REVIEW",
                        {
                            "repair_attempts": repair_attempt,
                            "error_category": "MAX_REPAIR_EXCEEDED",
                            "draft_path": current_draft_path,
                            "audit_path": audit_path,
                        },
                    )

                repair_attempt += 1
                logger.info(f"[{lesson_id}] Audit FAILED. Entering Repair round {repair_attempt}...")
                self.state_mgr.transition(
                    lesson_id,
                    "REPAIRING",
                    {"repair_attempts": repair_attempt},
                )

                # Run Repair
                res_repair = self._run_repair(
                    lesson_meta,
                    raw_content,
                    current_draft,
                    audit_report.get("findings", []),
                    attempt=repair_attempt,
                )
                if len(res_repair) == 3:
                    repaired_draft, repaired_path, repair_meta = res_repair
                    lesson_inferences.append(repair_meta)
                else:
                    repaired_draft, repaired_path = res_repair
                current_draft = repaired_draft
                current_draft_path = repaired_path
            else:
                # INCONCLUSIVE
                logger.warning(f"[{lesson_id}] Audit verdict is INCONCLUSIVE.")
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": "AUDIT_INCONCLUSIVE",
                        "audit_path": audit_path,
                    },
                )

        # STEP 4: FINALIZATION (IF PASS)
        if final_verdict == "PASS":
            safe_title = "".join(c if c.isalnum() else "_" for c in lesson_meta["title"])
            module_dir = os.path.join(self.modules_dir, lesson_meta["module_id"])
            os.makedirs(module_dir, exist_ok=True)
            final_path = os.path.join(module_dir, f"{lesson_id}_{safe_title}.md")

            # Atomic write to prevent partially written or interrupted files becoming PASS
            temp_final_path = f"{final_path}.tmp"
            with open(temp_final_path, "w", encoding="utf-8") as f:
                f.write(current_draft)
            os.replace(temp_final_path, final_path)

            if not os.path.exists(final_path):
                raise IOError(f"Failed to write final output file: {final_path}")

            # Stage assets in module directory so relative image links resolve from final Markdown
            module_assets_link = os.path.join(module_dir, "assets")
            if not os.path.exists(module_assets_link):
                try:
                    rel_to_assets = os.path.relpath(self.assets_dir, module_dir)
                    os.symlink(rel_to_assets, module_assets_link)
                except Exception as e:
                    logger.warning(f"Could not stage module assets symlink: {e}")

            final_sha256 = calculate_sha256(final_path)

            if not audit_path or not os.path.exists(audit_path):
                logger.error(f"[{lesson_id}] Missing audit report for PASS finalization: {audit_path}")
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": "MISSING_AUDIT_REPORT_FOR_PASS",
                        "final_path": final_path,
                        "final_sha256": final_sha256,
                    },
                )

            audit_sha256 = calculate_sha256(audit_path)
            if not audit_sha256:
                logger.error(f"[{lesson_id}] Empty audit sha256 for PASS finalization.")
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": "EMPTY_AUDIT_SHA256_FOR_PASS",
                        "final_path": final_path,
                        "final_sha256": final_sha256,
                    },
                )

            # Check audit binding to exact final SHA256
            if audit_report.get("audited_final_sha256") and audit_report.get("audited_final_sha256") != final_sha256:
                logger.error(
                    f"[{lesson_id}] Audit final SHA256 mismatch "
                    f"(report: {audit_report.get('audited_final_sha256')}, final: {final_sha256})"
                )
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": "AUDIT_FINAL_SHA256_MISMATCH",
                        "final_path": final_path,
                        "final_sha256": final_sha256,
                        "audit_path": audit_path,
                        "audit_sha256": audit_sha256,
                    },
                )

            inv_id = audit_report.get("audit_invocation_id") or last_audit_meta.get("invocation_id") or last_audit_meta.get("conversation_id")

            # Handle Mock Mode: transitions to MOCK_PASS, never production PASS
            if self.execution_mode == "mock":
                final_figs = extract_figures_from_markdown(current_draft)
                if final_figs:
                    proc_figs, vm_path, vm_sha = self.visual_asset_mgr.process_figures_for_lesson(
                        lesson_id=lesson_id,
                        figures=final_figs,
                        raw_source_content=raw_content,
                    )
                    last_vis = {
                        "manifest_path": vm_path,
                        "manifest_sha256": vm_sha,
                        "figures": proc_figs,
                        "draft_sha256": final_sha256,
                    }
                else:
                    last_vis = {
                        "manifest_path": None,
                        "manifest_sha256": None,
                        "figures": [],
                        "draft_sha256": final_sha256,
                    }
                self._last_lesson_visuals[lesson_id] = last_vis

                mock_updates = {
                    "final_path": final_path,
                    "final_sha256": final_sha256,
                    "draft_path": current_draft_path,
                    "audit_path": audit_path,
                    "audit_sha256": audit_sha256,
                    "audit_invocation_id": inv_id,
                    "model_verified": "NOT_APPLICABLE",
                    "evidence_class": "MOCK_SIMULATED",
                    "repair_attempts": repair_attempt,
                    "verdict": "PASS",
                }
                if last_vis.get("manifest_path"):
                    mock_updates["visual_manifest_path"] = last_vis["manifest_path"]
                    mock_updates["visual_manifest_sha256"] = last_vis["manifest_sha256"]
                    mock_updates["visual_figures"] = last_vis.get("figures", [])
                return self.state_mgr.transition(
                    lesson_id,
                    "MOCK_PASS",
                    mock_updates,
                )

            # Real AGY production finalization: model verification across all inferences is mandatory
            require_model_verification = True
            unverified_roles = []
            for inf in lesson_inferences:
                role_name = inf.get("role", "unknown")
                mv = inf.get("model_verified")
                if mv != "VERIFIED" or mv in ("NOT_VERIFIED", "MISMATCH", "NOT_APPLICABLE"):
                    unverified_roles.append(f"{role_name}:{mv}")

            if unverified_roles or getattr(self.adapter, "last_model_verified", None) in ("NOT_VERIFIED", "MISMATCH", "NOT_APPLICABLE"):
                logger.warning(
                    f"[{lesson_id}] PASS blocked: Model verification required but inference(s) not verified: {unverified_roles}"
                )
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": "MODEL_NOT_VERIFIED_FOR_PASS",
                        "final_path": final_path,
                        "final_sha256": final_sha256,
                        "audit_path": audit_path,
                        "audit_sha256": audit_sha256,
                        "unverified_roles": unverified_roles,
                    },
                )

            # Verify draft structural, fidelity, and visual integrity failures
            draft_issues = validate_draft_structure(
                current_draft,
                source_type=lesson_meta.get("source_type", ""),
                lesson_id=lesson_id,
                raw_source_content=raw_content,
                base_dir=self.output_dir,
                check_student_cleanliness=True,
            )
            blocking_draft_issues, _ = classify_draft_issues(draft_issues)
            if blocking_draft_issues:
                logger.error(
                    f"[{lesson_id}] Production PASS blocked: blocking draft integrity failure(s): {blocking_draft_issues}"
                )
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": f"BLOCKING_DRAFT_INTEGRITY_FAILURES: {blocking_draft_issues[0]}",
                        "final_path": final_path,
                        "final_sha256": final_sha256,
                        "draft_path": current_draft_path,
                        "audit_path": audit_path,
                        "audit_sha256": audit_sha256,
                        "blocking_draft_issues": blocking_draft_issues,
                    },
                )

            # Recalculate and strictly bind visual evidence for exact final draft
            final_figs = extract_figures_from_markdown(current_draft)
            if final_figs:
                proc_figs, vm_path, vm_sha = self.visual_asset_mgr.process_figures_for_lesson(
                    lesson_id=lesson_id,
                    figures=final_figs,
                    raw_source_content=raw_content,
                )
                last_vis = {
                    "manifest_path": vm_path,
                    "manifest_sha256": vm_sha,
                    "figures": proc_figs,
                    "draft_sha256": final_sha256,
                }
            else:
                last_vis = {
                    "manifest_path": None,
                    "manifest_sha256": None,
                    "figures": [],
                    "draft_sha256": final_sha256,
                }

            # Guard against silently replacing audited visual evidence with regenerated, materially different assets
            audited_vm_sha = audit_report.get("visual_manifest_sha256")
            audited_fig_count = audit_report.get("visual_figures_audited")
            if audited_vm_sha and last_vis.get("manifest_sha256") != audited_vm_sha:
                logger.error(
                    f"[{lesson_id}] Production PASS blocked: final visual manifest SHA256 '{last_vis.get('manifest_sha256')}' "
                    f"does not match audited visual manifest SHA256 '{audited_vm_sha}'"
                )
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": "AUDITED_VISUAL_EVIDENCE_REPLACED",
                        "final_path": final_path,
                        "final_sha256": final_sha256,
                        "audit_path": audit_path,
                        "audit_sha256": audit_sha256,
                        "visual_manifest_sha256": last_vis.get("manifest_sha256"),
                        "audited_visual_manifest_sha256": audited_vm_sha,
                    },
                )

            if audited_fig_count is not None and len(final_figs) != audited_fig_count:
                logger.error(
                    f"[{lesson_id}] Production PASS blocked: final figure count {len(final_figs)} "
                    f"does not match audited figure count {audited_fig_count}"
                )
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": "AUDITED_VISUAL_EVIDENCE_REPLACED",
                        "final_path": final_path,
                        "final_sha256": final_sha256,
                        "audit_path": audit_path,
                        "audit_sha256": audit_sha256,
                        "visual_figures_count": len(final_figs),
                        "audited_visual_figures_count": audited_fig_count,
                    },
                )

            self._last_lesson_visuals[lesson_id] = last_vis

            # Record production PASS with Controller audit receipt validation
            try:
                return self.state_mgr.record_audit_verdict(
                    lesson_id=lesson_id,
                    verdict="PASS",
                    audit_path=audit_path,
                    expected_final_sha256=final_sha256,
                    audit_invocation_id=inv_id,
                    notes="Automated production PASS finalization",
                    require_model_verification=True,
                    final_path=final_path,
                    visual_manifest_path=last_vis.get("manifest_path"),
                    visual_manifest_sha256=last_vis.get("manifest_sha256"),
                    visual_figures=last_vis.get("figures"),
                    quality_rubric_version=audit_report.get("quality_rubric_version"),
                    lesson_type=lesson_meta.get("source_type"),
                    source_status=lesson_meta.get("status"),
                )
            except Exception as e:
                logger.error(f"[{lesson_id}] Production PASS recording rejected: {e}")
                return self.state_mgr.transition(
                    lesson_id,
                    "NEEDS_HUMAN_REVIEW",
                    {
                        "error_category": f"AUDIT_RECEIPT_PROVENANCE_FAILED: {e}",
                        "final_path": final_path,
                        "final_sha256": final_sha256,
                        "audit_path": audit_path,
                        "audit_sha256": audit_sha256,
                    },
                )

        return self.state_mgr.load_checkpoint(lesson_id) or {}

    def _api_candidate_issues(self, lesson_meta, content):
        """Validate the complete rendered candidate before any Auditor request."""
        from course_harness.visual import validate_automatic_visuals
        source_path = os.path.join(self.source_dir, lesson_meta["relative_path"])
        if getattr(self, "_manifest_sha256", None) and calculate_sha256(self.manifest_path) != self._manifest_sha256:
            raise ApiIntegrityError("Manifest changed during lesson execution")
        if calculate_sha256(source_path) != lesson_meta["source_sha256"]:
            raise ManifestStaleError("Source changed during lesson execution")
        if compute_prompt_config_hash(self.prompts_dir, self.config_path) != self.prompt_config_hash:
            raise ApiIntegrityError("Prompts/config changed during lesson execution")
        issues = validate_draft_structure(
            content, lesson_meta["source_type"], lesson_id=lesson_meta["lesson_id"],
            raw_source_content=self._api_raw_content,
            base_dir=self.output_dir, check_student_cleanliness=True,
        )
        visuals = self._last_lesson_visuals.get(lesson_meta["lesson_id"], {})
        issues.extend(validate_automatic_visuals(content, visuals, self.output_dir))
        if lesson_meta["source_type"] in ("VIDEO_TRANSCRIPT", "READING") and not visuals.get("figures"):
            issues.append("Missing required automatic educational diagram")
        return classify_draft_issues(issues)[0]

    def _process_api_lesson(self, lesson_meta, raw_content, reset=False):
        """Automatic production using the existing drafting, rendering, audit and quality gates."""
        lesson_id = lesson_meta["lesson_id"]
        source_sha = lesson_meta["source_sha256"]
        self._api_raw_content = raw_content
        if lesson_meta["status"] not in ("AVAILABLE", "INCOMPLETE"):
            return self.state_mgr.transition(lesson_id, "BLOCKED", {"error_category": "SOURCE_UNAVAILABLE"})
        if not reset and self.state_mgr.is_resumable_pass(
            lesson_id, source_sha, lesson_type=lesson_meta["source_type"], source_status=lesson_meta["status"]
        ):
            return self.state_mgr.load_checkpoint(lesson_id)
        previous = self.state_mgr.load_checkpoint(lesson_id) or {}
        can_reuse = (not reset and previous.get("source_sha256") == source_sha
                     and previous.get("prompt_config_hash") == self.prompt_config_hash
                     and previous.get("execution_mode") == "gemini_api"
                     and previous.get("draft_path") and previous.get("draft_sha256"))
        if can_reuse:
            if not os.path.isfile(previous["draft_path"]) or calculate_sha256(previous["draft_path"]) != previous["draft_sha256"]:
                raise ApiIntegrityError("Checkpoint candidate checksum mismatch")
            if not previous.get("inference_metadata") or not all(verified_api_receipt(m) for m in previous["inference_metadata"]):
                raise ApiIntegrityError("Checkpoint inference evidence is missing or modified")
        self.state_mgr.initialize_lesson_state(
            lesson_id, source_sha, model_id=self.model_id, effort="high", execution_mode="gemini_api",
            lesson_type=lesson_meta["source_type"], source_status=lesson_meta["status"],
        )
        repairs = previous.get("repair_attempts", 0) if can_reuse else 0
        if can_reuse:
            with open(previous["draft_path"], encoding="utf-8") as draft:
                current, draft_path = draft.read(), previous["draft_path"]
            inferences = previous["inference_metadata"]
            visuals = previous.get("candidate_visuals", {})
            self._last_lesson_visuals[lesson_id] = visuals
        else:
            current, draft_path, worker_meta = self._run_worker_draft(lesson_meta, raw_content)
            inferences = [worker_meta]

        def save_candidate(preserve_audit=False):
            updates = {} if preserve_audit else {"audited_draft_sha256": None, "auditor_metadata": None}
            return self.state_mgr.transition(lesson_id, "DRAFTED", {
                **updates,
                "execution_mode": "gemini_api", "draft_path": draft_path, "draft_sha256": sha256(current),
                "draft_version": repairs + 1, "repair_attempts": repairs,
                "inference_metadata": inferences, "candidate_visuals": self._last_lesson_visuals.get(lesson_id, {}),
                "evidence_class": inferences[-1]["evidence_class"],
                "human_review_required": True, "visual_review_required": bool(extract_figures_from_markdown(current)),
            })

        save_candidate(preserve_audit=can_reuse)
        while True:
            blocking = self._api_candidate_issues(lesson_meta, current)
            if blocking:
                findings = [{"finding_id": f"STRUCT-{i}", "severity": "BLOCKING", "category": "STRUCTURE",
                             "source_locator": "original source", "draft_locator": "candidate",
                             "description": issue, "required_action": issue} for i, issue in enumerate(blocking)]
                report = {"verdict": "FAIL", "findings": findings}
            else:
                reusable_audit = can_reuse and previous.get("audited_draft_sha256") == sha256(current)
                if reusable_audit:
                    audit_path = previous.get("audit_path")
                    if not audit_path or calculate_sha256(audit_path) != previous.get("audit_sha256"):
                        raise ApiIntegrityError("Saved audit checksum mismatch")
                    with open(audit_path, encoding="utf-8") as audit_file:
                        raw_audit = audit_file.read()
                    report, _ = self.validator.validate_report(raw_audit, expected_lesson_id=lesson_id,
                        lesson_type=lesson_meta["source_type"], source_status=lesson_meta["status"])
                    audit_meta = previous["auditor_metadata"]
                    if not verified_api_receipt(audit_meta):
                        raise ApiIntegrityError("Saved Auditor evidence mismatch")
                else:
                    try:
                        report, audit_path, audit_meta = self._run_auditor(lesson_meta, raw_content, current, repairs + 1)
                    except ValidationError as exc:
                        return self.state_mgr.transition(lesson_id, "NEEDS_HUMAN_REVIEW", {
                            "error_category": f"AUDIT_VALIDATION_ERROR: {exc}", "verdict": "INCONCLUSIVE"})
                    self.state_mgr.transition(lesson_id, "AUDITED", {
                        "audit_path": audit_path, "audit_sha256": calculate_sha256(audit_path),
                        "audited_draft_sha256": sha256(current), "auditor_metadata": audit_meta,
                        "audit_invocation_id": report["audit_invocation_id"], "verdict": report["verdict"],
                    })
                if report["verdict"] == "PASS":
                    eligible, reason = is_production_quality_eligible(report,
                        lesson_type=lesson_meta["source_type"], source_status=lesson_meta["status"])
                    if not eligible:
                        raise ApiIntegrityError("Validated PASS failed production quality gates: " + reason)
                    # Recheck immutable inputs and rendered bytes at the publication boundary.
                    if self._api_candidate_issues(lesson_meta, current):
                        raise ApiIntegrityError("Candidate changed after independent audit")
                    visuals = self._last_lesson_visuals.get(lesson_id, {})
                    module_dir = os.path.join(self.modules_dir, lesson_meta["module_id"])
                    os.makedirs(module_dir, exist_ok=True)
                    asset_link = os.path.join(module_dir, "assets")
                    if not os.path.exists(asset_link):
                        os.symlink(os.path.relpath(self.assets_dir, module_dir), asset_link)
                    # StateManager verifies the full production receipt before publication.
                    result = self.state_mgr.record_audit_verdict(
                        lesson_id, verdict="PASS", audit_path=audit_path, final_path=draft_path, persist=False,
                        expected_final_sha256=sha256(current), audit_invocation_id=report["audit_invocation_id"],
                        require_model_verification=True, visual_manifest_path=visuals.get("manifest_path"),
                        visual_manifest_sha256=visuals.get("manifest_sha256"), visual_figures=visuals.get("figures", []),
                        quality_rubric_version=report.get("quality_rubric_version"),
                        lesson_type=lesson_meta["source_type"], source_status=lesson_meta["status"],
                    )
                    final_path = os.path.join(module_dir, f"{lesson_id}.md")
                    temporary = final_path + ".tmp"
                    with open(temporary, "w", encoding="utf-8") as final:
                        final.write(current)
                    os.replace(temporary, final_path)
                    result.update(final_path=final_path, human_review_required=True,
                                  visual_review_required=bool(visuals.get("figures")))
                    self.state_mgr.save_checkpoint(lesson_id, result)
                    return result
            if report["verdict"] != "FAIL":
                return self.state_mgr.transition(lesson_id, "NEEDS_HUMAN_REVIEW", {"error_category": "AUDIT_INCONCLUSIVE"})
            if repairs >= self.max_repair_rounds:
                return self.state_mgr.transition(lesson_id, "NEEDS_HUMAN_REVIEW", {
                    "repair_attempts": repairs, "error_category": "MAX_REPAIR_EXCEEDED", "verdict": "FAIL",
                    "blocking_draft_issues": blocking,
                })
            repairs += 1
            self.state_mgr.transition(lesson_id, "REPAIRING", {"repair_attempts": repairs})
            try:
                current, draft_path, repair_meta = self._run_repair(
                    lesson_meta, raw_content, current, report.get("findings", []), repairs)
            except (GeminiApiError, KeyboardInterrupt):
                self.state_mgr.transition(lesson_id, "DRAFTED", {"repair_attempts": repairs - 1})
                raise
            inferences.append(repair_meta)
            save_candidate()
            can_reuse = False

    def _run_worker_draft(self, lesson_meta: Dict[str, Any], raw_content: str) -> Tuple[str, str, Dict[str, Any]]:
        """Prepares prompt and runs the Worker."""
        lesson_id = lesson_meta["lesson_id"]
        template = self._load_prompt_template("worker")

        locators_summary = ", ".join(
            loc["locator"] for loc in lesson_meta.get("locators", [])[:10]
        )

        prompt = (
            template.replace("{{LESSON_ID}}", lesson_id)
            .replace("{{COURSE_ID}}", self.course_id)
            .replace("{{MODULE_ID}}", lesson_meta["module_id"])
            .replace("{{MODULE_TITLE}}", lesson_meta.get("module_title", ""))
            .replace("{{LESSON_TITLE}}", lesson_meta["title"])
            .replace("{{SOURCE_TYPE}}", lesson_meta["source_type"])
            .replace("{{LOCATORS}}", locators_summary)
            .replace("{{RAW_CONTENT}}", raw_content)
        )

        if self.execution_mode == "gemini_api":
            seed = self.config.get("workflow", {}).get("seed_drafts", {}).get(lesson_id)
            if seed:
                if seed.get("source_sha256") != lesson_meta["source_sha256"] or calculate_sha256(seed["path"]) != seed["sha256"]:
                    raise ApiIntegrityError("Seed draft/source checksum mismatch")
                if seed.get("visual_manifest_path") and calculate_sha256(seed["visual_manifest_path"]) != seed.get("visual_manifest_sha256"):
                    raise ApiIntegrityError("Seed visual manifest checksum mismatch")
                with open(seed["path"], encoding="utf-8") as sf:
                    prompt += "\nExisting candidate to recheck against the original source. Return the complete Vietnamese lesson, not a verdict:\n" + sf.read()

        if self.execution_mode == "gemini_api":
            prompt += "\nSource status: " + lesson_meta["status"] + ". Explain INCOMPLETE source limitations in Vietnamese; do not invent missing material."
        worker_inv_id = f"inv-worker-{lesson_id}-att1-{uuid.uuid4().hex[:12]}"
        response_text, meta = self.adapter.invoke(
            prompt=prompt,
            role="worker",
            lesson_id=lesson_id,
            fresh_session=True,
            step_attempt=1,
            invocation_id=worker_inv_id,
        )

        clean_text = response_text.strip()
        # Verify transport JSON was not leaked into lesson markdown
        if clean_text.startswith("{") and '"status"' in clean_text and '"response"' in clean_text:
            raise CliExecutionError("LEAKED_TRANSPORT_JSON: Worker output contains raw transport JSON envelope")

        if clean_text.startswith("```markdown") and clean_text.endswith("```"):
            clean_text = clean_text[len("```markdown") : -3].strip()

        draft_filename = f"{lesson_id}_draft_v1.md" if self.execution_mode != "gemini_api" else f"{worker_inv_id}.md"
        draft_path = os.path.join(self.drafts_dir, draft_filename)
        with open(draft_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        # Process and extract visual assets if present
        draft_sha = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
        figures = extract_figures_from_markdown(clean_text)
        if figures:
            proc_figs, vm_path, vm_sha = self.visual_asset_mgr.process_figures_for_lesson(
                lesson_id=lesson_id,
                figures=figures,
                raw_source_content=raw_content,
            )
            # Reconcile/normalize draft image paths against rendered assets
            normalized_text = normalize_markdown_asset_paths(clean_text, proc_figs, lesson_id=lesson_id)
            if normalized_text != clean_text:
                clean_text = normalized_text
                draft_sha = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
                with open(draft_path, "w", encoding="utf-8") as f:
                    f.write(clean_text)

            self._last_lesson_visuals[lesson_id] = {
                "manifest_path": vm_path,
                "manifest_sha256": vm_sha,
                "figures": proc_figs,
                "draft_sha256": draft_sha,
            }
        else:
            # Explicitly clear stale lesson visual metadata when current draft contains no figures
            self._last_lesson_visuals[lesson_id] = {
                "manifest_path": None,
                "manifest_sha256": None,
                "figures": [],
                "draft_sha256": draft_sha,
            }

        # Validate draft structure
        issues = validate_draft_structure(
            clean_text,
            lesson_meta["source_type"],
            lesson_id=lesson_id,
            raw_source_content=raw_content,
            base_dir=self.output_dir,
            check_student_cleanliness=True,
        )
        blocking, warnings = classify_draft_issues(issues)
        if warnings:
            logger.warning(f"[{lesson_id}] Draft heuristic warnings: {warnings}")
        if blocking:
            logger.error(f"[{lesson_id}] Draft blocking integrity issues: {blocking}")

        return clean_text, draft_path, meta

    def _run_auditor(
        self,
        lesson_meta: Dict[str, Any],
        raw_content: str,
        draft_content: str,
        attempt: int,
    ) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
        """Runs Independent Auditor with completely fresh session."""
        lesson_id = lesson_meta["lesson_id"]
        template = self._load_prompt_template("auditor")

        prompt = (
            template.replace("{{LESSON_ID}}", lesson_id)
            .replace("{{SOURCE_TYPE}}", lesson_meta["source_type"])
            .replace("{{RAW_CONTENT}}", raw_content)
            .replace("{{DRAFT_CONTENT}}", draft_content)
        )

        inv_id = f"inv-auditor-{lesson_id}-att{attempt}-{uuid.uuid4().hex[:12]}"

        if self.execution_mode == "gemini_api":
            visuals = self._last_lesson_visuals.get(lesson_id, {})
            prompt += "\nExact candidate SHA256: " + sha256(draft_content)
            prompt += "\nSource SHA256: " + lesson_meta["source_sha256"]
            prompt += "\nSource status: " + lesson_meta["status"]
            prompt += "\nAuthoritative visual manifest: " + json.dumps(visuals, ensure_ascii=False)
            for figure in visuals.get("figures", []):
                asset = os.path.join(self.output_dir, figure["rendered_asset_path"])
                with open(asset, encoding="utf-8") as svg:
                    prompt += "\nRendered SVG evidence:\n" + svg.read()
            prompt += "\nEvaluate this exact candidate independently. SVG source inspection cannot establish human visual acceptance."

        raw_response, meta = self.adapter.invoke(
            prompt=prompt,
            role="auditor",
            lesson_id=lesson_id,
            fresh_session=True,
            output_format="json",
            step_attempt=attempt,
            invocation_id=inv_id,
        )

        # Validate structured audit report
        try:
            validated_report, warnings = self.validator.validate_report(
                raw_response,
                expected_lesson_id=lesson_id,
                lesson_type=lesson_meta.get("source_type"),
                source_status=lesson_meta.get("status"),
            )
            for w in warnings:
                logger.warning(f"[{lesson_id}] Audit warning: {w}")
        except ValidationError as e:
            logger.error(f"[{lesson_id}] Auditor output failed validation: {e}")
            # If Auditor output violates schema, save raw output for investigation and treat as INCONCLUSIVE
            bad_audit_path = os.path.join(self.audits_dir, f"{lesson_id}_audit_v{attempt}_INVALID.txt")
            with open(bad_audit_path, "w", encoding="utf-8") as f:
                f.write(raw_response)
            raise

        # Bind audited final content SHA256 and invocation evidence
        audited_final_sha256 = hashlib.sha256(draft_content.encode("utf-8")).hexdigest()
        if self.execution_mode == "gemini_api" and validated_report.get("audited_final_sha256") != audited_final_sha256:
            raise ApiIntegrityError("Auditor did not attest the exact candidate SHA256")
        validated_report["audited_final_sha256"] = audited_final_sha256
        validated_report["audit_invocation_id"] = inv_id
        if meta.get("model_verified"):
            validated_report["model_verification"] = meta["model_verified"]

        # Ensure visual evidence corresponds to exact current draft
        audited_final_sha256 = hashlib.sha256(draft_content.encode("utf-8")).hexdigest()
        lesson_vis = self._last_lesson_visuals.get(lesson_id)
        if not lesson_vis or lesson_vis.get("draft_sha256") != audited_final_sha256:
            # Recalculate visual evidence for current draft
            curr_figs = extract_figures_from_markdown(draft_content)
            if curr_figs:
                proc_figs, vm_path, vm_sha = self.visual_asset_mgr.process_figures_for_lesson(
                    lesson_id=lesson_id,
                    figures=curr_figs,
                    raw_source_content=raw_content,
                )
                lesson_vis = {
                    "manifest_path": vm_path,
                    "manifest_sha256": vm_sha,
                    "figures": proc_figs,
                    "draft_sha256": audited_final_sha256,
                }
            else:
                lesson_vis = {
                    "manifest_path": None,
                    "manifest_sha256": None,
                    "figures": [],
                    "draft_sha256": audited_final_sha256,
                }
            self._last_lesson_visuals[lesson_id] = lesson_vis

        # Bind visual assets evidence if figures present
        if lesson_vis and lesson_vis.get("figures"):
            if lesson_vis.get("manifest_sha256"):
                validated_report["visual_manifest_sha256"] = lesson_vis["manifest_sha256"]
            validated_report["visual_figures_audited"] = len(lesson_vis.get("figures", []))
        else:
            validated_report.pop("visual_manifest_sha256", None)
            validated_report["visual_figures_audited"] = 0

        audit_filename = f"{lesson_id}_audit_v{attempt}.json" if self.execution_mode != "gemini_api" else f"{inv_id}.json"
        audit_path = os.path.join(self.audits_dir, audit_filename)
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(validated_report, f, indent=2, ensure_ascii=False)

        audit_report_sha256 = calculate_sha256(audit_path)

        # Persist trusted Controller audit receipt
        raw_full_path = os.path.join(self.source_dir, lesson_meta.get("relative_path", ""))
        src_sha = lesson_meta.get("source_sha256")
        if not src_sha and os.path.exists(raw_full_path):
            src_sha = calculate_sha256(raw_full_path)

        receipt_data = {
            "invocation_id": inv_id,
            "role": "auditor",
            "lesson_id": lesson_id,
            "lesson_type": lesson_meta.get("source_type"),
            "source_status": lesson_meta.get("status"),
            "execution_mode": meta.get("execution_mode", self.execution_mode),
            "provider": meta.get("provider", "agy" if self.execution_mode == "automated_cli" else "mock"),
            "evidence_class": meta.get("evidence_class", "MOCK_SIMULATED" if self.execution_mode == "mock" else "REAL_AGY_VERIFIED"),
            "model_requested": self.model_id,
            "model_reported": meta.get("model_reported"),
            "model_verified": meta.get("model_verified", "NOT_VERIFIED"),
            "terminal_status": meta.get("terminal_status", "SUCCESS" if meta.get("model_verified") == "VERIFIED" else "SIMULATED" if self.execution_mode == "mock" else "ERROR"),
            "audited_final_sha256": audited_final_sha256,
            "source_sha256": src_sha,
            "prompt_config_hash": self.prompt_config_hash,
            "audit_report_sha256": audit_report_sha256,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if self.execution_mode in {"gemini_api", "automated_cli"}:
            receipt_data.update({key: meta.get(key) for key in (
                "thinking_level", "raw_response_path", "raw_response_sha256", "response_sha256",
                "response_id", "request_id", "started_at", "completed_at", "usage", "usage_metadata",
                "conversation_id", "prompt_sha256", "model_verification_evidence",
            )})
        self.state_mgr.save_audit_receipt(receipt_data)

        return validated_report, audit_path, meta

    def _run_repair(
        self,
        lesson_meta: Dict[str, Any],
        raw_content: str,
        draft_content: str,
        findings: List[Dict[str, Any]],
        attempt: int,
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Runs Repair agent to fix findings."""
        lesson_id = lesson_meta["lesson_id"]
        template = self._load_prompt_template("repair")

        prompt = (
            template.replace("{{LESSON_ID}}", lesson_id)
            .replace("{{SOURCE_TYPE}}", lesson_meta["source_type"])
            .replace("{{RAW_CONTENT}}", raw_content)
            .replace("{{DRAFT_CONTENT}}", draft_content)
            .replace("{{AUDIT_FINDINGS}}", json.dumps(findings, indent=2, ensure_ascii=False))
        )

        if self.execution_mode == "gemini_api":
            prompt += "\nSource status: " + lesson_meta["status"] + ". Preserve explicit Vietnamese limitations for INCOMPLETE sources."
        repair_inv_id = f"inv-repair-{lesson_id}-att{attempt}-{uuid.uuid4().hex[:12]}"
        repaired_text, meta = self.adapter.invoke(
            prompt=prompt,
            role="repair",
            lesson_id=lesson_id,
            fresh_session=True,
            step_attempt=attempt,
            invocation_id=repair_inv_id,
        )

        clean_text = repaired_text.strip()
        # Verify transport JSON was not leaked into lesson markdown
        if clean_text.startswith("{") and '"status"' in clean_text and '"response"' in clean_text:
            raise CliExecutionError("LEAKED_TRANSPORT_JSON: Repair output contains raw transport JSON envelope")

        if clean_text.startswith("```markdown") and clean_text.endswith("```"):
            clean_text = clean_text[len("```markdown") : -3].strip()

        version = attempt + 1
        repaired_filename = f"{lesson_id}_draft_v{version}.md" if self.execution_mode != "gemini_api" else f"{repair_inv_id}.md"
        repaired_path = os.path.join(self.drafts_dir, repaired_filename)
        with open(repaired_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        # Process and extract visual assets if present
        draft_sha = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
        figures = extract_figures_from_markdown(clean_text)
        if figures:
            proc_figs, vm_path, vm_sha = self.visual_asset_mgr.process_figures_for_lesson(
                lesson_id=lesson_id,
                figures=figures,
                raw_source_content=raw_content,
            )
            # Reconcile/normalize draft image paths against rendered assets
            normalized_text = normalize_markdown_asset_paths(clean_text, proc_figs, lesson_id=lesson_id)
            if normalized_text != clean_text:
                clean_text = normalized_text
                draft_sha = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
                with open(repaired_path, "w", encoding="utf-8") as f:
                    f.write(clean_text)

            self._last_lesson_visuals[lesson_id] = {
                "manifest_path": vm_path,
                "manifest_sha256": vm_sha,
                "figures": proc_figs,
                "draft_sha256": draft_sha,
            }
        else:
            # Explicitly clear stale lesson visual metadata when current draft contains no figures
            self._last_lesson_visuals[lesson_id] = {
                "manifest_path": None,
                "manifest_sha256": None,
                "figures": [],
                "draft_sha256": draft_sha,
            }

        # Validate draft structure after repair
        issues = validate_draft_structure(
            clean_text,
            lesson_meta["source_type"],
            lesson_id=lesson_id,
            raw_source_content=raw_content,
            base_dir=self.output_dir,
            check_student_cleanliness=True,
        )
        blocking, warnings = classify_draft_issues(issues)
        if warnings:
            logger.warning(f"[{lesson_id}] Repaired draft heuristic warnings: {warnings}")
        if blocking:
            logger.error(f"[{lesson_id}] Repaired draft blocking integrity issues: {blocking}")

        return clean_text, repaired_path, meta

    def run_pilot(self, reset: bool = False) -> Dict[str, Any]:
        """Runs the three vertical slice pilot lessons (P1, P2, P3)."""
        if self.execution_mode == "automated_cli":
            raise BlockedExecutionError(AGY_BATCH_BLOCK_REASON)
        logger.info(f"=== STARTING VERTICAL SLICE PILOT ({len(PILOT_LESSON_IDS)} LESSONS) ===")
        results = {}
        for lesson_id in PILOT_LESSON_IDS:
            try:
                res = self.process_lesson(lesson_id, reset=reset)
                results[lesson_id] = {
                    "status": res.get("status"),
                    "verdict": res.get("verdict"),
                    "repair_attempts": res.get("repair_attempts", 0),
                    "final_path": res.get("final_path"),
                }
            except Exception as e:
                logger.error(f"[{lesson_id}] Failed: {e}", exc_info=True)
                results[lesson_id] = {"status": "FAILED", "error": str(e)}

        summary_file = os.path.join(self.evidence_dir, "pilot_summary.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Pilot execution finished. Summary saved to {summary_file}")
        return results


def main():
    parser = argparse.ArgumentParser(description="Course Harness v1 Orchestrator")
    parser.add_argument("--config", default="course_harness/config.yaml", help="Path to config.yaml")
    parser.add_argument("--mode", choices=["gemini_api", "automated_cli", "manual_cli_handoff", "mock"], help="Execution mode override")
    parser.add_argument("--inspect", action="store_true", help="Inspect and index raw course sources")
    parser.add_argument("--pilot", action="store_true", help="Run the 3 pilot lessons (P1, P2, P3)")
    parser.add_argument("--lesson", help="Process a single lesson ID (e.g. M01-L07)")
    parser.add_argument("--module", help="Process all lessons in a module (e.g. M01)")
    parser.add_argument("--reset", action="store_true", help="Force reset existing checkpoints")
    parser.add_argument("--report", action="store_true", help="Generate pipeline status report")
    parser.add_argument("--readiness", action="store_true", help="Offline provider policy assessment; no CLI calls")
    parser.add_argument("--batch", action="store_true", help="Launch Batch Scheduler orchestrator")
    parser.add_argument("--batch-dry-run", action="store_true", help="Preview batch plan (0 provider calls)")
    parser.add_argument("--batch-lessons", nargs="+", help="Specific lesson IDs for batch processing (max 5)")
    parser.add_argument("--batch-select", type=int, default=5, help="Select up to N eligible lessons (max 5)")
    parser.add_argument("--allow-incomplete", action="store_true", help="Permit INCOMPLETE sources with documented scope")

    args = parser.parse_args()

    if args.readiness:
        print(json.dumps(provider_readiness(args.mode, args.config), indent=2))
        return 0

    try:
        controller = CourseHarnessController(config_path=args.config, mode_override=args.mode)

        if args.inspect:
            env_info = controller.verify_system()
            manifest = controller.get_manifest(force_refresh=True)
            print("\n=== SYSTEM VERIFICATION ===")
            print(json.dumps(env_info, indent=2))
            print("\n=== COURSE INGESTION SUMMARY ===")
            print(f"Course ID: {manifest['course_id']}")
            print(f"Total Modules: {manifest['total_modules']}")
            print(f"Total Lessons: {manifest['total_lessons']}")
            print("\nModules breakdown:")
            for mid, mdata in manifest["modules"].items():
                print(f"  [{mid}] {mdata['title']}: {mdata['lesson_count']} lessons")
            return 0

        if args.report:
            manifest = controller.get_manifest()
            print("\n=== CHECKPOINT STATUS REPORT ===")
            passed = 0
            human_accepted = 0
            human_review = 0
            blocked = 0
            pending = 0
            mock_pass = 0
            for lid in manifest["lessons"].keys():
                chk = controller.state_mgr.load_checkpoint(lid)
                st = chk.get("status", "PENDING") if chk else "PENDING"
                if st == "PASS":
                    passed += 1
                elif st == "HUMAN_ACCEPTED":
                    human_accepted += 1
                elif st == "MOCK_PASS":
                    mock_pass += 1
                elif st == "NEEDS_HUMAN_REVIEW":
                    human_review += 1
                elif st == "BLOCKED":
                    blocked += 1
                else:
                    pending += 1
            print(f"Total: {len(manifest['lessons'])} | PASS: {passed} | HUMAN_ACCEPTED: {human_accepted} | MOCK_PASS: {mock_pass} | NEEDS_HUMAN_REVIEW: {human_review} | BLOCKED: {blocked} | PENDING: {pending}")
            return 0

        if args.batch_dry_run:
            from course_harness.batch import BatchScheduler
            scheduler = BatchScheduler(config_path=args.config, mode_override=args.mode, controller=controller)
            plan = scheduler.plan_batch(
                requested_ids=args.batch_lessons,
                limit=args.batch_select,
                allow_incomplete=args.allow_incomplete,
            )
            print("\n=======================================================")
            print(f"             BATCH 1 DRY-RUN PLAN ({plan.batch_id})")
            print("=======================================================")
            print(f"Course: {plan.course_id}")
            print(f"Manifest SHA256: {plan.manifest_sha256}")
            print(f"Candidate Count: {len(plan.candidate_lessons)}")
            for idx, c in enumerate(plan.candidate_lessons, 1):
                print(f"  {idx}. [{c.lesson_id}] ({c.source_type}, status: {c.source_status}) - {c.title}")
            return 0

        if args.batch:
            if controller.execution_mode == "automated_cli":
                raise BlockedExecutionError(AGY_BATCH_BLOCK_REASON)
            from course_harness.batch import BatchScheduler
            scheduler = BatchScheduler(config_path=args.config, mode_override=args.mode, controller=controller)
            plan = scheduler.plan_batch(
                requested_ids=args.batch_lessons,
                limit=args.batch_select,
                allow_incomplete=args.allow_incomplete,
            )
            res = scheduler.execute_batch(plan)
            print(json.dumps(res, indent=2))
            return 0

        if controller.execution_mode == "automated_cli" and (args.pilot or args.module):
            raise BlockedExecutionError(AGY_BATCH_BLOCK_REASON)

        # Verify environment before running inferences
        controller.verify_system()

        if args.pilot:
            controller.run_pilot(reset=args.reset)
            return 0

        if args.lesson:
            if controller.execution_mode == "gemini_api":
                from course_harness.batch import BatchScheduler
                scheduler = BatchScheduler(config_path=args.config, controller=controller)
                result = scheduler.execute_batch(scheduler.plan_batch(requested_ids=[args.lesson], allow_incomplete=args.allow_incomplete))
                print(json.dumps(result, indent=2))
            else:
                controller.process_lesson(args.lesson, reset=args.reset)
            return 0

        if args.module:
            manifest = controller.get_manifest()
            mod_data = manifest.get("modules", {}).get(args.module)
            if not mod_data:
                print(f"Module '{args.module}' not found.")
                return 1
            for lid in mod_data["lesson_ids"]:
                controller.process_lesson(lid, reset=args.reset)
            return 0

        parser.print_help()
        return 0

    except BlockedExecutionError as e:
        print(f"\nCRITICAL POLICY BLOCKER: {e}", file=sys.stderr)
        return 3
    except ManifestStaleError as e:
        print(f"\nINTEGRITY ERROR: {e}", file=sys.stderr)
        return 4
    except ModelUnavailableError as e:
        print(f"\nCRITICAL BLOCKER: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
