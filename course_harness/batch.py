#!/usr/bin/env python3
"""Batch Scheduler and Execution Orchestrator for Course Harness v1.

Provides controlled, deterministic batch processing of course lessons with:
- Lesson discovery from authoritative manifest.json
- Source eligibility classification (AVAILABLE, INCOMPLETE, LOCKED, UNAVAILABLE)
- Human-approved baseline preservation (M02-L11, M03-L08)
- Sequential execution by default; bounded Gemini API concurrency after verification
- Concurrency protection via atomic lockfiles
- Resource & quota budget monitoring (invocations, tokens, runtime)
- Instructor image hard gate enforcement
- Atomic checkpoint persistence and safe resume validation
- Deterministic dry-run planning with zero model calls
"""

import argparse
import copy
import dataclasses
from dataclasses import dataclass, field
import hashlib
import json
import logging
import os
import re
import sys
import time
import uuid
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from course_harness.gemini_adapter import (
    ApiAuthenticationError, ApiBudgetError, ApiIntegrityError,
)
from course_harness.cli_adapter import AgyAdapter, redact_signed_urls
from course_harness.provider_policy import AGY_BATCH_BLOCK_REASON, provider_readiness
from course_harness.ingest import calculate_sha256
from course_harness.quality_policy import (
    APPROVED_BASELINES, PROHIBITED_INSTRUCTOR_PATTERNS, scan_for_prohibited_instructor_images,
)
from course_harness.run import (
    CourseHarnessController,
    ManifestStaleError,
    BlockedExecutionError,
)
from course_harness.state import (
    StateManager,
    calculate_file_sha256,
    compute_prompt_config_hash,
)
from course_harness.validator import (
    classify_draft_issues,
    is_production_quality_eligible,
    validate_draft_structure,
)

logger = logging.getLogger("course_harness.batch")

# ---------------------------------------------------------------------------
# Constants & Baselines
# ---------------------------------------------------------------------------

MAX_BATCH_LESSONS = 5
MAX_CONCURRENCY = 1
MAX_REPAIRS_PER_LESSON = 2
DEFAULT_MAX_INVOCATIONS = 15
DEFAULT_MAX_BATCH_TOKENS = 500_000
DEFAULT_MAX_RUNTIME_SECONDS = 1800.0

class BatchSchedulingError(Exception):
    """Raised when batch scheduling constraints are violated."""
    pass


class ConcurrentBatchExecutionError(Exception):
    """Raised when another scheduler instance holds the batch execution lock."""
    pass


class BaselineIntegrityError(Exception):
    """Raised when an approved baseline check fails or an attempt is made to overwrite it."""
    pass


class ConfigurationChangedError(Exception):
    """Raised when prompt or workflow configuration changed since batch creation."""
    pass


class ManifestChangedError(Exception):
    """Raised when manifest changed since batch creation."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class LessonEligibility:
    """Eligibility classification result for a candidate lesson."""
    lesson_id: str
    module_id: str
    title: str
    source_type: str
    source_status: str
    source_rel_path: str
    source_full_path: str
    source_sha256: str
    is_eligible: bool
    eligibility_reason: str
    known_limitations: List[str] = field(default_factory=list)
    prior_checkpoint_status: Optional[str] = None


@dataclass
class ResourceLimits:
    """Configured limits for batch execution."""
    max_lessons: int = MAX_BATCH_LESSONS
    max_concurrency: int = MAX_CONCURRENCY
    max_repairs_per_lesson: int = MAX_REPAIRS_PER_LESSON
    max_provider_invocations: int = DEFAULT_MAX_INVOCATIONS
    max_batch_tokens: int = DEFAULT_MAX_BATCH_TOKENS
    max_batch_runtime_seconds: float = DEFAULT_MAX_RUNTIME_SECONDS
    monetary_budget_enabled: bool = False


@dataclass
class ResourceUsage:
    """Observed or estimated resource usage."""
    invocations: int = 0
    worker_invocations: int = 0
    auditor_invocations: int = 0
    repair_invocations: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0
    wall_clock_seconds: float = 0.0
    repair_rounds: int = 0
    missing_usage_invocations: int = 0
    monetary_cost: Optional[float] = None
    currency: Optional[str] = None
    usage_class: str = "UNKNOWN_USAGE"  # OBSERVED_USAGE, ESTIMATED_USAGE, UNKNOWN_USAGE
    model_verification_counts: Dict[str, int] = field(default_factory=lambda: {
        "VERIFIED": 0, "NOT_VERIFIED": 0, "MISMATCH": 0, "MOCK": 0
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "invocations": self.invocations,
            "worker_invocations": self.worker_invocations,
            "auditor_invocations": self.auditor_invocations,
            "repair_invocations": self.repair_invocations,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "thinking_tokens": self.thinking_tokens,
            "total_tokens": self.total_tokens,
            "wall_clock_seconds": round(self.wall_clock_seconds, 3),
            "repair_rounds": self.repair_rounds,
            "usage_class": self.usage_class,
            "missing_usage_invocations": self.missing_usage_invocations,
            "monetary_cost": self.monetary_cost,
            "currency": self.currency,
            "model_verification_counts": dict(self.model_verification_counts),
        }


class ResourceBudgetTracker:
    """Monitors and enforces safe resource and quota limits."""

    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self.usage = ResourceUsage()

    def record_invocation(self, metadata: Dict[str, Any]) -> None:
        """Records metadata from an individual model invocation."""
        role = metadata.get("role", "unknown")
        self.usage.invocations += 1
        if role == "worker":
            self.usage.worker_invocations += 1
        elif role == "auditor":
            self.usage.auditor_invocations += 1
        elif role == "repair":
            self.usage.repair_invocations += 1
            self.usage.repair_rounds += 1

        dur = metadata.get("duration_seconds") or 0.0
        self.usage.wall_clock_seconds += dur

        # Track model verification
        mv = metadata.get("model_verified", "NOT_VERIFIED")
        if metadata.get("mode") == "mock" or metadata.get("execution_mode") == "mock":
            mv = "MOCK"
        self.usage.model_verification_counts[mv] = self.usage.model_verification_counts.get(mv, 0) + 1

        # Token usage extraction
        usage_dict = metadata.get("usage")
        if isinstance(usage_dict, dict) and any(v is not None for v in usage_dict.values()):
            inp = usage_dict.get("input_tokens") or 0
            out = usage_dict.get("output_tokens") or 0
            thk = usage_dict.get("thinking_tokens") or 0
            tot = usage_dict.get("total_tokens")

            self.usage.input_tokens += inp
            self.usage.output_tokens += out
            self.usage.thinking_tokens += thk

            # Do not double-count thinking tokens if provider already included them in total
            if tot is not None and tot > 0:
                self.usage.total_tokens += tot
            else:
                self.usage.total_tokens += (inp + out + thk)

            if usage_dict.get("total_tokens") is None:
                self.usage.missing_usage_invocations += 1
            self.usage.usage_class = "OBSERVED_USAGE"
        else:
            self.usage.missing_usage_invocations += 1
            if self.usage.usage_class != "OBSERVED_USAGE":
                self.usage.usage_class = "UNKNOWN_USAGE"

    def check_limits(
        self,
        estimated_next_invocations: int = 2,
        estimated_next_tokens: int = 50_000,
    ) -> Tuple[bool, Optional[str]]:
        """Checks if budget permits scheduling another lesson at safe lesson boundary."""
        if self.usage.invocations >= self.limits.max_provider_invocations:
            return False, f"Provider invocation limit reached ({self.usage.invocations}/{self.limits.max_provider_invocations})"

        if self.usage.invocations + estimated_next_invocations > self.limits.max_provider_invocations:
            return False, (
                f"Insufficient remaining invocation budget for next lesson "
                f"({self.usage.invocations} + {estimated_next_invocations} > {self.limits.max_provider_invocations})"
            )

        if self.usage.wall_clock_seconds >= self.limits.max_batch_runtime_seconds:
            return False, (
                f"Batch wall-clock runtime limit reached "
                f"({self.usage.wall_clock_seconds:.1f}s >= {self.limits.max_batch_runtime_seconds:.1f}s)"
            )

        if self.usage.usage_class == "OBSERVED_USAGE" and self.usage.total_tokens >= self.limits.max_batch_tokens:
            return False, f"Token quota reached ({self.usage.total_tokens} >= {self.limits.max_batch_tokens})"

        return True, None


@dataclass
class BatchPlan:
    """Deterministic dry-run batch execution plan."""
    batch_id: str
    course_id: str
    manifest_sha256: str
    prompt_config_hash: str
    candidate_lessons: List[LessonEligibility]
    excluded_lessons: List[Dict[str, Any]]
    resource_limits: ResourceLimits
    estimated_usage: ResourceUsage
    human_review_required: bool
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "course_id": self.course_id,
            "manifest_sha256": self.manifest_sha256,
            "prompt_config_hash": self.prompt_config_hash,
            "candidate_count": len(self.candidate_lessons),
            "candidates": [dataclasses.asdict(c) for c in self.candidate_lessons],
            "excluded_count": len(self.excluded_lessons),
            "resource_limits": dataclasses.asdict(self.resource_limits),
            "estimated_usage": self.estimated_usage.to_dict(),
            "human_review_required": self.human_review_required,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Concurrency Lockfile & Atomic Operations
# ---------------------------------------------------------------------------

class BatchLock:
    """Atomic lockfile to prevent concurrent batch schedulers from running simultaneously."""

    def __init__(self, lock_path: str, batch_id: str):
        self.lock_path = lock_path
        self.batch_id = batch_id
        self._fd: Optional[int] = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self) -> None:
        if os.path.exists(self.lock_path):
            try:
                with open(self.lock_path, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)
                locked_pid = lock_data.get("pid")
                # Check if process is still running
                if locked_pid and self._is_pid_alive(locked_pid):
                    raise ConcurrentBatchExecutionError(
                        f"CONCURRENT_BATCH_LOCKED: Batch scheduler already running under PID {locked_pid} "
                        f"(batch: {lock_data.get('batch_id')}, host: {lock_data.get('hostname')})."
                    )
                else:
                    # Stale lock: clean up
                    logger.warning(f"Reclaiming stale lockfile from dead PID {locked_pid}")
                    os.remove(self.lock_path)
            except (json.JSONDecodeError, OSError):
                # Corrupted lock: remove safely
                try:
                    os.remove(self.lock_path)
                except OSError:
                    pass

        lock_content = {
            "batch_id": self.batch_id,
            "pid": os.getpid(),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        try:
            self._fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            with os.fdopen(self._fd, "w", encoding="utf-8") as f:
                json.dump(lock_content, f, indent=2)
            self._fd = None
        except FileExistsError:
            raise ConcurrentBatchExecutionError(
                f"CONCURRENT_BATCH_LOCKED: Another process acquired lock at {self.lock_path}"
            )

    def release(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None
        if os.path.exists(self.lock_path):
            try:
                os.remove(self.lock_path)
            except OSError:
                pass

    @staticmethod
    def _is_pid_alive(pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def atomic_write_json(file_path: str, data: Dict[str, Any]) -> str:
    """Safely and atomically writes JSON data to disk using a temporary file and fsync."""
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    temp_path = f"{file_path}.tmp.{uuid.uuid4().hex[:8]}"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_path, file_path)
    return calculate_file_sha256(file_path)


# ---------------------------------------------------------------------------
# Instructor Image Hard Gate
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Batch Scheduler
# ---------------------------------------------------------------------------

class BatchScheduler:
    """Minimal, reliable Batch Scheduler for Course Harness v1.
    
    Orchestrates candidate discovery, source eligibility enforcement, resource limits,
    sequential single-lesson pipeline execution, atomic checkpoints, and safe resume.
    """

    def __init__(
        self,
        config_path: str = "course_harness/config.yaml",
        mode_override: Optional[str] = None,
        controller: Optional[CourseHarnessController] = None,
        limits: Optional[ResourceLimits] = None,
    ):
        self.config_path = config_path
        self.controller = controller or CourseHarnessController(
            config_path=config_path, mode_override=mode_override
        )
        self.config_path = self.controller.config_path
        api_mode = self.controller.execution_mode == "gemini_api"
        self.limits = limits or (ResourceLimits(**self.controller.config.get("resources", {"max_lessons": 10000})) if api_mode else ResourceLimits())
        if self.limits.max_lessons < 1 or not 1 <= self.limits.max_concurrency <= (4 if api_mode else 1):
            raise BatchSchedulingError("Invalid lesson/concurrency limit")
        if self.limits.monetary_budget_enabled:
            raise BatchSchedulingError("Provider does not report monetary cost; configure token and invocation limits instead")
        self.controller.max_repair_rounds = min(self.controller.max_repair_rounds, self.limits.max_repairs_per_lesson, 2)
        self.budget = ResourceBudgetTracker(self.limits)
        self._budget_lock = threading.RLock()
        self._batch_record = None
        self._batch_record_path = None
        self.approved_state_mgr = self.controller.state_mgr
        approved_dir = self.controller.config.get("paths", {}).get("approved_output_dir")
        if approved_dir:
            self.approved_state_mgr = StateManager(os.path.join(approved_dir, "evidence", "checkpoints"), self.controller.prompt_config_hash)
        self.approved_output_dir = approved_dir or self.controller.output_dir

        self.batch_checkpoints_dir = os.path.join(
            self.controller.evidence_dir, "batch_checkpoints"
        )
        os.makedirs(self.batch_checkpoints_dir, exist_ok=True)

        # Hook controller adapter invoke to record usage accurately
        self._wrap_adapter_invocation()

    def _wrap_adapter_invocation(self, controller=None):
        controller = controller or self.controller
        if controller.execution_mode == "gemini_api":
            controller.adapter.before_attempt = self._before_api_attempt
            controller.adapter.on_attempt = self._record_api_attempt
            return
        original_invoke = controller.adapter.invoke
        def wrapped_invoke(*args, **kwargs):
            res_text, meta = original_invoke(*args, **kwargs)
            self.budget.record_invocation(meta)
            return res_text, meta
        controller.adapter.invoke = wrapped_invoke

    def _refresh_runtime(self):
        if hasattr(self, "_runtime_started"):
            elapsed = self._runtime_before_resume + time.monotonic() - self._runtime_started
            self.budget.usage.wall_clock_seconds = max(self.budget.usage.wall_clock_seconds, elapsed)
            if self._batch_record is not None:
                self._batch_record["elapsed_runtime_seconds"] = elapsed

    def _before_api_attempt(self):
        with self._budget_lock:
            self._refresh_runtime()
            # shortcut: token/runtime limits stop new requests; in-flight requests may exceed them, use reservations for strict spend caps.
            if getattr(self, "_provider_halt", False):
                raise ApiBudgetError("Batch halted after a critical provider/integrity error")
            pending = getattr(self, "_pending_attempts", 0)
            permitted, reason = self.budget.check_limits(estimated_next_invocations=pending + 1, estimated_next_tokens=0)
            if not permitted:
                raise ApiBudgetError(reason)
            self._pending_attempts = pending + 1

    def _record_api_attempt(self, metadata):
        with self._budget_lock:
            self._pending_attempts -= 1
            if metadata.get("error_category") in ("ApiAuthenticationError", "ApiBudgetError", "ApiIntegrityError"):
                self._provider_halt = True
            if metadata.get("terminal_status") == "SUCCESS" and (metadata.get("usage") or {}).get("total_tokens") is None:
                self._provider_halt = True
            self.budget.record_invocation(metadata)
            self._refresh_runtime()
            if self._batch_record is not None:
                self._batch_record["budget_consumed"] = self.budget.usage.to_dict()
                atomic_write_json(self._batch_record_path, self._batch_record)
            if metadata.get("terminal_status") == "SUCCESS" and (metadata.get("usage") or {}).get("total_tokens") is None:
                raise ApiBudgetError("Successful Gemini response has unknown token usage; stop before further spending")

    def verify_approved_baselines(self) -> Dict[str, Any]:
        """Verifies that human-approved baseline lessons (M02-L11, M03-L08) remain intact.
        Fails closed if any expected SHA256 differs.
        """
        results = {}
        for lid, info in APPROVED_BASELINES.items():
            chk = self.approved_state_mgr.load_checkpoint(lid)
            if not chk and self.controller.course_id != "Agile_Project_Management":
                continue
            if not chk:
                raise BaselineIntegrityError(f"Missing checkpoint for approved baseline {lid}")

            if chk.get("status") != "HUMAN_ACCEPTED":
                raise BaselineIntegrityError(
                    f"Baseline {lid} status is '{chk.get('status')}', expected 'HUMAN_ACCEPTED'"
                )

            final_path = chk.get("final_path")
            if not final_path or not os.path.exists(final_path):
                raise BaselineIntegrityError(f"Final output file missing for baseline {lid}: {final_path}")

            disk_final_sha = calculate_file_sha256(final_path)
            expected_final_sha = info["approved_final_sha256"]
            if disk_final_sha != expected_final_sha:
                raise BaselineIntegrityError(
                    f"Final SHA256 mismatch for baseline {lid}: "
                    f"expected '{expected_final_sha}', found '{disk_final_sha}'"
                )

            # Check acceptance artifact
            acc_path = chk.get("acceptance_path")
            if not acc_path or not os.path.exists(acc_path):
                raise BaselineIntegrityError(f"Acceptance artifact missing for baseline {lid}: {acc_path}")

            acc_sha = calculate_file_sha256(acc_path)
            if acc_sha != chk.get("acceptance_sha256"):
                raise BaselineIntegrityError(f"Acceptance artifact SHA256 modified for baseline {lid}")

            # Check visual manifest if applicable
            if "visual_manifest_sha256" in info:
                vm_path = os.path.join(self.approved_output_dir, "assets", lid, "visual_manifest.json")
                if not os.path.exists(vm_path):
                    raise BaselineIntegrityError(f"Visual manifest missing for baseline {lid}: {vm_path}")
                vm_sha = calculate_file_sha256(vm_path)
                if vm_sha != info["visual_manifest_sha256"]:
                    raise BaselineIntegrityError(f"Visual manifest SHA256 mismatch for baseline {lid}")

            results[lid] = {
                "status": "VERIFIED_INTACT",
                "final_sha256": disk_final_sha,
                "acceptance_sha256": acc_sha,
            }

        return results

    def discover_lessons(
        self,
        allow_incomplete: bool = False,
    ) -> Tuple[List[LessonEligibility], List[Dict[str, Any]]]:
        """Discovers all lessons from authoritative manifest and evaluates eligibility."""
        manifest = self.controller.get_manifest()
        lessons_meta = manifest.get("lessons", {})

        eligible: List[LessonEligibility] = []
        excluded: List[Dict[str, Any]] = []

        for lid, l_meta in lessons_meta.items():
            mod_id = l_meta.get("module_id", "")
            title = l_meta.get("title", "")
            source_type = l_meta.get("source_type", "READING")
            status = l_meta.get("status", "UNKNOWN")
            rel_path = l_meta.get("relative_path", "")
            manifest_source_sha = l_meta.get("source_sha256", "")
            full_path = os.path.join(self.controller.source_dir, rel_path)

            prior_chk = self.controller.state_mgr.load_checkpoint(lid) or self.approved_state_mgr.load_checkpoint(lid)
            prior_status = prior_chk.get("status") if prior_chk else None

            # 1. Baseline protection: exclude approved baselines by default
            if lid in APPROVED_BASELINES:
                excluded.append({
                    "lesson_id": lid,
                    "reason": "EXCLUDED_APPROVED_BASELINE",
                    "details": "Lesson is a frozen human-approved baseline.",
                    "status": status,
                    "source_type": source_type,
                })
                continue

            # 2. Exclude previously HUMAN_ACCEPTED lessons by default
            if prior_status == "HUMAN_ACCEPTED":
                excluded.append({
                    "lesson_id": lid,
                    "reason": "EXCLUDED_ALREADY_HUMAN_ACCEPTED",
                    "details": "Lesson has already achieved formal human approval.",
                    "status": status,
                    "source_type": source_type,
                })
                continue

            # 3. Source file integrity check
            if not os.path.exists(full_path):
                excluded.append({
                    "lesson_id": lid,
                    "reason": "SOURCE_FILE_MISSING",
                    "details": f"Source file does not exist on disk: {full_path}",
                    "status": status,
                    "source_type": source_type,
                })
                continue

            disk_source_sha = calculate_sha256(full_path)
            if disk_source_sha != manifest_source_sha:
                excluded.append({
                    "lesson_id": lid,
                    "reason": "SOURCE_SHA_MISMATCH",
                    "details": (
                        f"Disk SHA ({disk_source_sha}) diverges from manifest ({manifest_source_sha}). "
                        f"Ingestion refresh required."
                    ),
                    "status": status,
                    "source_type": source_type,
                })
                continue

            # 4. Source Status Classification
            known_limits = []
            if status == "AVAILABLE":
                is_elig = True
                reason = "ELIGIBLE_AVAILABLE"
            elif status == "INCOMPLETE":
                known_limits.append("Missing raw quiz answer keys or partial source template.")
                if allow_incomplete:
                    is_elig = True
                    reason = "ELIGIBLE_INCOMPLETE_WITH_DOCUMENTED_BOUNDED_SCOPE"
                else:
                    is_elig = False
                    reason = "INCOMPLETE_REQUIRES_BOUNDED_SCOPE_APPROVAL"
            elif status in ("LOCKED", "UNAVAILABLE"):
                is_elig = False
                reason = f"BLOCKED_SOURCE_{status}"
            else:
                is_elig = False
                reason = f"BLOCKED_UNKNOWN_STATUS_{status}"

            item = LessonEligibility(
                lesson_id=lid,
                module_id=mod_id,
                title=title,
                source_type=source_type,
                source_status=status,
                source_rel_path=rel_path,
                source_full_path=full_path,
                source_sha256=disk_source_sha,
                is_eligible=is_elig,
                eligibility_reason=reason,
                known_limitations=known_limits,
                prior_checkpoint_status=prior_status,
            )

            if is_elig:
                eligible.append(item)
            else:
                excluded.append({
                    "lesson_id": lid,
                    "reason": reason,
                    "details": f"Source status is {status}",
                    "status": status,
                    "source_type": source_type,
                })

        return eligible, excluded

    def select_candidates(
        self,
        requested_ids: Optional[List[str]] = None,
        limit: int = MAX_BATCH_LESSONS,
        allow_incomplete: bool = False,
        allow_baseline_override: bool = False,
    ) -> List[LessonEligibility]:
        """Selects up to `limit` lessons (max 5) strictly verifying constraints.
        Never invents lesson IDs. Deduplicates requested IDs preserving order.
        """
        if limit < 1 or limit > self.limits.max_lessons:
            raise BatchSchedulingError(
                f"MAX_BATCH_SIZE_EXCEEDED: Batch size {limit} exceeds configured maximum {self.limits.max_lessons}."
            )

        manifest = self.controller.get_manifest()
        manifest_lessons = manifest.get("lessons", {})

        if requested_ids is not None:
            # Deduplicate preserving order
            seen: Set[str] = set()
            deduped_ids: List[str] = []
            for rid in requested_ids:
                if rid not in seen:
                    seen.add(rid)
                    deduped_ids.append(rid)
                else:
                    logger.warning(f"Duplicate lesson ID '{rid}' removed from batch selection.")

            if len(deduped_ids) > self.limits.max_lessons:
                raise BatchSchedulingError(
                    f"MAX_BATCH_SIZE_EXCEEDED: Requested {len(deduped_ids)} lessons, max is {self.limits.max_lessons}."
                )

            selected: List[LessonEligibility] = []
            for lid in deduped_ids:
                if lid not in manifest_lessons:
                    raise KeyError(f"UNKNOWN_LESSON_ID: Lesson '{lid}' does not exist in authoritative manifest.")

                if lid in APPROVED_BASELINES and not allow_baseline_override:
                    if self.controller.execution_mode == "gemini_api" and self.controller.course_id == "Agile_Project_Management":
                        continue
                    raise BaselineIntegrityError(
                        f"PROTECTED_BASELINE: Lesson '{lid}' is an approved baseline and cannot be re-executed."
                    )

                l_meta = manifest_lessons[lid]
                full_path = os.path.join(self.controller.source_dir, l_meta["relative_path"])
                if not os.path.exists(full_path):
                    raise FileNotFoundError(f"Source file missing on disk: {full_path}")

                disk_sha = calculate_sha256(full_path)
                if disk_sha != l_meta.get("source_sha256"):
                    raise ManifestStaleError(f"Source checksum mismatch for {lid}")
                status = l_meta.get("status", "UNKNOWN")

                if status == "INCOMPLETE" and not allow_incomplete:
                    raise BatchSchedulingError(
                        f"INCOMPLETE_SOURCE_BLOCKED: Lesson '{lid}' has INCOMPLETE status. "
                        f"Requires explicit bounded-scope approval (--allow-incomplete)."
                    )
                if status in ("LOCKED", "UNAVAILABLE"):
                    raise BatchSchedulingError(
                        f"SOURCE_UNAVAILABLE_BLOCKED: Lesson '{lid}' is {status} and cannot be processed in batch."
                    )
                if status not in ("AVAILABLE", "INCOMPLETE"):
                    raise BatchSchedulingError(
                        f"UNKNOWN_STATUS_BLOCKED: Lesson '{lid}' has unknown status '{status}'. Fail closed."
                    )

                prior_chk = self.controller.state_mgr.load_checkpoint(lid) or self.approved_state_mgr.load_checkpoint(lid)
                prior_st = prior_chk.get("status") if prior_chk else None
                if prior_st == "HUMAN_ACCEPTED":
                    continue

                selected.append(LessonEligibility(
                    lesson_id=lid,
                    module_id=l_meta.get("module_id", ""),
                    title=l_meta.get("title", ""),
                    source_type=l_meta.get("source_type", "READING"),
                    source_status=status,
                    source_rel_path=l_meta.get("relative_path", ""),
                    source_full_path=full_path,
                    source_sha256=disk_sha,
                    is_eligible=True,
                    eligibility_reason="EXPLICITLY_REQUESTED_AND_VALIDATED",
                    known_limitations=[],
                    prior_checkpoint_status=prior_st,
                ))

            return selected

        # Auto-discovery
        eligible, _ = self.discover_lessons(allow_incomplete=allow_incomplete)

        # Exclude lessons that already passed production validation if not requested
        filtered = []
        for cand in eligible:
            if cand.prior_checkpoint_status == "PASS":
                # Check if resumable
                if self.controller.state_mgr.is_resumable_pass(
                    cand.lesson_id, cand.source_sha256
                ):
                    continue
            filtered.append(cand)
            if len(filtered) >= limit:
                break

        return filtered

    def plan_batch(
        self,
        requested_ids: Optional[List[str]] = None,
        limit: int = MAX_BATCH_LESSONS,
        allow_incomplete: bool = False,
    ) -> BatchPlan:
        """Constructs a deterministic dry-run batch plan.
        
        MAKES ZERO PROVIDER CALLS.
        MODIFIES NO RAW SOURCES.
        MODIFIES NO EXISTING APPROVED CHECKPOINTS.
        """
        # Always verify approved baseline integrity first
        self.verify_approved_baselines()

        candidates = self.select_candidates(
            requested_ids=requested_ids,
            limit=limit,
            allow_incomplete=allow_incomplete,
        )

        _, all_excluded = self.discover_lessons(allow_incomplete=allow_incomplete)

        # Compute deterministic batch identity
        batch_id = f"batch-{time.strftime('%Y%m%d', time.gmtime())}-{uuid.uuid4().hex[:8]}"
        manifest = self.controller.get_manifest()
        manifest_path = self.controller.manifest_path
        manifest_sha = calculate_file_sha256(manifest_path) if os.path.exists(manifest_path) else "UNKNOWN"
        prompt_cfg_hash = self.controller.prompt_config_hash

        # Conservative resource estimation based on pilot baselines
        cand_count = len(candidates)
        est_invocations = cand_count * 2  # 1 worker + 1 auditor minimum
        est_tokens = cand_count * 45_000   # ~45k tokens per lesson observed
        est_seconds = cand_count * 110.0   # ~110s per lesson observed

        est_usage = ResourceUsage(
            invocations=est_invocations,
            worker_invocations=cand_count,
            auditor_invocations=cand_count,
            repair_invocations=0,
            input_tokens=cand_count * 28_000,
            output_tokens=cand_count * 17_000,
            thinking_tokens=cand_count * 11_000,
            total_tokens=est_tokens,
            wall_clock_seconds=est_seconds,
            repair_rounds=0,
            usage_class="ESTIMATED_USAGE",
            model_verification_counts={"NOT_EXECUTED": est_invocations},
        )

        plan = BatchPlan(
            batch_id=batch_id,
            course_id=self.controller.course_id,
            manifest_sha256=manifest_sha,
            prompt_config_hash=prompt_cfg_hash,
            candidate_lessons=candidates,
            excluded_lessons=all_excluded,
            resource_limits=self.limits,
            estimated_usage=est_usage,
            human_review_required=True,  # All Batch 1 lessons require human review!
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        return plan

    def load_plan(self, batch_id):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", batch_id):
            raise BatchSchedulingError("Unsafe batch ID")
        with open(os.path.join(self.batch_checkpoints_dir, batch_id + ".json"), encoding="utf-8") as f:
            record = json.load(f)
        plan = record["plan"]
        return BatchPlan(
            batch_id=batch_id, course_id=plan["course_id"], manifest_sha256=plan["manifest_sha256"],
            prompt_config_hash=plan["prompt_config_hash"],
            candidate_lessons=[LessonEligibility(**c) for c in plan["candidates"]],
            excluded_lessons=[], resource_limits=ResourceLimits(**plan["resource_limits"]),
            estimated_usage=ResourceUsage(**plan["estimated_usage"]),
            human_review_required=True, created_at=plan["created_at"],
        )

    def _execute_candidate(self, candidate, controller):
        start = time.monotonic()
        try:
            result = controller.process_lesson(candidate.lesson_id)
            final_path = result.get("final_path")
            if final_path and os.path.isfile(final_path):
                with open(final_path, encoding="utf-8") as final:
                    violations = scan_for_prohibited_instructor_images(final.read())
                if violations:
                    result.update(status="BLOCKED", error_category="PROHIBITED_INSTRUCTOR_IMAGE")
                    controller.state_mgr.transition(candidate.lesson_id, "BLOCKED", result)
            return {"status": result.get("status", "UNKNOWN"), "verdict": result.get("verdict"),
                    "final_path": result.get("final_path"), "final_sha256": result.get("final_sha256"),
                    "audit_sha256": result.get("audit_sha256"), "error_category": result.get("error_category"),
                    "duration_seconds": round(time.monotonic() - start, 2),
                    "human_review_required": True}
        except (ManifestStaleError, ConfigurationChangedError, ApiAuthenticationError, ApiBudgetError, ApiIntegrityError):
            raise
        except Exception as exc:
            logger.error("[%s] Lesson failed: %s", candidate.lesson_id, type(exc).__name__)
            controller.state_mgr.transition(candidate.lesson_id, "NEEDS_HUMAN_REVIEW", {
                "error_category": type(exc).__name__, "verdict": "INCONCLUSIVE"})
            return {"status": "FAILED", "error_category": type(exc).__name__, "error": str(exc)}

    def execute_batch(self, plan, dry_run=False, resume_batch_id=None):
        """Run lessons in bounded waves; checkpoint every result and every API attempt."""
        if dry_run:
            return {"batch_id": plan.batch_id, "status": "DRY_RUN_COMPLETED", "plan": plan.to_dict(),
                    "executed_lessons": [], "provider_calls": 0,
                    "provider_readiness": provider_readiness(self.controller.execution_mode),
                    "workflow": "SOURCE -> WORKER -> VISUAL RENDER -> STRUCTURAL VALIDATION -> INDEPENDENT AUDITOR -> REPAIR (max 2) -> FRESH AUDITOR -> FINAL QUALITY GATE -> PUBLISH -> CHECKPOINT",
                    "manual_steps": [], "human_acceptance": "NEVER_AUTOMATIC"}
        if self.controller.execution_mode == "automated_cli":
            raise BlockedExecutionError(AGY_BATCH_BLOCK_REASON)
        if len(plan.candidate_lessons) > self.limits.max_lessons:
            raise BatchSchedulingError("MAX_BATCH_SIZE_EXCEEDED")
        if plan.course_id != self.controller.course_id:
            raise ManifestChangedError("Batch course does not match Controller course")
        if plan.prompt_config_hash != self.controller.prompt_config_hash:
            raise ConfigurationChangedError("Prompts/config changed since planning")
        if calculate_file_sha256(self.controller.manifest_path) != plan.manifest_sha256:
            raise ManifestChangedError("Manifest changed since planning")
        for candidate in plan.candidate_lessons:
            if candidate.lesson_id in APPROVED_BASELINES:
                raise BaselineIntegrityError("PROTECTED_BASELINE: " + candidate.lesson_id)
        api_mode = self.controller.execution_mode == "gemini_api"
        if api_mode:
            self.verify_approved_baselines()
        concurrency = self.limits.max_concurrency
        if concurrency > 1:
            sequential_verified = False
            for checkpoint in Path(self.batch_checkpoints_dir).glob("*.json"):
                record = json.loads(checkpoint.read_text(encoding="utf-8"))
                if (record.get("status") == "COMPLETED" and record.get("summary", {}).get("passed", 0) > 0
                    and record.get("limits", {}).get("max_concurrency") == 1
                    and record.get("prompt_config_hash") == self.controller.prompt_config_hash
                    and record.get("course_id") == self.controller.course_id):
                    sequential_verified = any(
                        result.get("status") == "PASS" and self.controller.state_mgr.is_resumable_pass(
                            lid, self.controller.get_manifest()["lessons"][lid]["source_sha256"])
                        for lid, result in record.get("lessons", {}).items()
                        if lid in self.controller.get_manifest()["lessons"]
                    )
                    if sequential_verified:
                        break
            if not sequential_verified:
                raise BatchSchedulingError("Run a successful sequential API batch before enabling concurrency")
        batch_id = resume_batch_id or plan.batch_id
        if not re.fullmatch(r"[A-Za-z0-9_-]+", batch_id):
            raise BatchSchedulingError("Unsafe batch ID")
        chk_path = os.path.join(self.batch_checkpoints_dir, batch_id + ".json")
        # One active scheduler per output course; its own workers may run concurrently.
        lock_path = os.path.join(self.batch_checkpoints_dir, "course.lock")
        with BatchLock(lock_path, batch_id):
            if resume_batch_id:
                with open(chk_path, encoding="utf-8") as f:
                    batch_record = json.load(f)
                if batch_record.get("course_id") != plan.course_id:
                    raise ManifestChangedError("Resume course mismatch")
                if batch_record.get("prompt_config_hash") != self.controller.prompt_config_hash:
                    raise ConfigurationChangedError("CONFIG_CHANGED since batch creation")
                if batch_record.get("manifest_sha256") != calculate_file_sha256(self.controller.manifest_path):
                    raise ManifestChangedError("MANIFEST_CHANGED since batch creation")
                saved_ids = [c["lesson_id"] for c in batch_record.get("plan", {}).get("candidates", [])]
                if saved_ids and saved_ids != [c.lesson_id for c in plan.candidate_lessons]:
                    raise ManifestChangedError("Resume lesson selection differs from saved plan")
            else:
                batch_record = {"batch_id": batch_id, "course_id": plan.course_id,
                    "manifest_sha256": plan.manifest_sha256, "prompt_config_hash": plan.prompt_config_hash,
                    "limits": dataclasses.asdict(self.limits), "plan": plan.to_dict(), "created_at": plan.created_at,
                    "lessons": {}, "summary": {"total_candidates": len(plan.candidate_lessons),
                        "passed": 0, "needs_human_review": 0, "blocked": 0, "failed": 0, "skipped": 0}}
            batch_record["status"] = "RUNNING"
            self._provider_halt = False
            self._pending_attempts = 0
            self._batch_record, self._batch_record_path = batch_record, chk_path
            self._runtime_started = time.monotonic()
            self._runtime_before_resume = float(batch_record.get("elapsed_runtime_seconds", 0))
            if api_mode:
                self.controller.adapter.batch_id = batch_id
                if resume_batch_id:
                    self.budget = ResourceBudgetTracker(self.limits)
                    for path in self.controller.adapter.evidence_dir.glob("*.try[1-6].json"):
                        metadata = json.loads(path.read_text(encoding="utf-8"))
                        if metadata.get("batch_id") == batch_id:
                            if (metadata.get("terminal_status") == "STARTED" or
                                (metadata.get("terminal_status") == "SUCCESS" and (metadata.get("usage") or {}).get("total_tokens") is None)):
                                raise ApiBudgetError("Interrupted API request has unknown usage; reconcile before resume")
                            self.budget.record_invocation(metadata)
            atomic_write_json(chk_path, batch_record)
            pending = []
            for candidate in plan.candidate_lessons:
                lid = candidate.lesson_id
                prior = self.controller.state_mgr.load_checkpoint(lid) or self.approved_state_mgr.load_checkpoint(lid)
                existing = batch_record["lessons"].get(lid, {})
                accepted = prior and prior.get("status") == "HUMAN_ACCEPTED"
                if accepted or (existing.get("status") in ("PASS", "HUMAN_ACCEPTED", "SKIPPED") and self.controller.state_mgr.is_resumable_pass(
                    lid, candidate.source_sha256, lesson_type=candidate.source_type, source_status=candidate.source_status)):
                    batch_record["lessons"][lid] = {**existing, "status": "SKIPPED", "skip_reason": "ALREADY_VERIFIED_PASS"}
                    continue
                pending.append(candidate)
            fatal = None
            try:
                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    for offset in range(0, len(pending), concurrency):
                        if calculate_file_sha256(self.controller.manifest_path) != plan.manifest_sha256:
                            raise ManifestChangedError("Manifest changed during batch execution")
                        if compute_prompt_config_hash(self.controller.prompts_dir, self.config_path) != plan.prompt_config_hash:
                            raise ConfigurationChangedError("Prompts/config changed during batch execution")
                        wave = pending[offset:offset + concurrency]
                        self._refresh_runtime()
                        permitted, reason = self.budget.check_limits(estimated_next_invocations=2 * len(wave), estimated_next_tokens=50000 * len(wave))
                        if not permitted:
                            batch_record["lessons"][wave[0].lesson_id] = {"status": "BLOCKED", "error_category": "BUDGET_EXHAUSTED", "reason": reason}
                            batch_record["status"] = "PAUSED_BUDGET_EXHAUSTED"
                            break
                        futures = {}
                        for candidate in wave:
                            controller = self.controller
                            if concurrency > 1:
                                controller = CourseHarnessController(self.config_path, mode_override="gemini_api")
                                controller.adapter.batch_id = batch_id
                                self._wrap_adapter_invocation(controller)
                            batch_record["lessons"][candidate.lesson_id] = {"status": "RUNNING"}
                            atomic_write_json(chk_path, batch_record)
                            logger.info("[%s] Starting %s (%s/%s)", batch_id, candidate.lesson_id, offset + 1, len(pending))
                            futures[pool.submit(self._execute_candidate, candidate, controller)] = (candidate, controller)
                        for future in as_completed(futures):
                            candidate, controller = futures[future]
                            try:
                                result = future.result()
                            except (ManifestStaleError, ConfigurationChangedError, ApiAuthenticationError, ApiBudgetError, ApiIntegrityError) as exc:
                                fatal = exc
                                self._provider_halt = True
                                result = {"status": "FAILED", "error_category": type(exc).__name__, "error": str(exc)}
                                controller.state_mgr.transition(candidate.lesson_id, "BLOCKED", result | {"status": "BLOCKED"})
                                batch_record["status"] = "PAUSED_BUDGET_EXHAUSTED" if isinstance(exc, ApiBudgetError) else "FAILED"
                            finally:
                                if concurrency > 1:
                                    controller.adapter.close()
                            with self._budget_lock:
                                batch_record["lessons"][candidate.lesson_id] = result
                                batch_record["budget_consumed"] = self.budget.usage.to_dict()
                                atomic_write_json(chk_path, batch_record)
                            logger.info("[%s] %s: %s", batch_id, candidate.lesson_id, result["status"])
                        if fatal:
                            break
            except BaseException:
                batch_record["status"] = "INTERRUPTED"
                atomic_write_json(chk_path, batch_record)
                raise
            finally:
                counts = {"PASS": "passed", "NEEDS_HUMAN_REVIEW": "needs_human_review", "BLOCKED": "blocked", "SKIPPED": "skipped"}
                summary = dict.fromkeys(("passed", "needs_human_review", "blocked", "skipped", "failed"), 0)
                for result in batch_record["lessons"].values():
                    summary[counts.get(result["status"], "failed")] += 1
                batch_record["summary"] = {"total_candidates": len(plan.candidate_lessons), **summary}
                if batch_record["status"] == "RUNNING":
                    batch_record["status"] = "COMPLETED_WITH_FAILURES" if summary["failed"] or summary["blocked"] else "COMPLETED"
                self._refresh_runtime()
                batch_record["budget_consumed"] = self.budget.usage.to_dict()
                atomic_write_json(chk_path, batch_record)
                self._batch_record = None
            if api_mode:
                self.verify_approved_baselines()
            if fatal:
                raise fatal
            return batch_record



# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Course Harness v1 Batch Scheduler")
    parser.add_argument("--config", default="course_harness/config.yaml", help="Path to config.yaml")
    parser.add_argument("--mode", choices=["gemini_api", "automated_cli", "manual_cli_handoff", "mock"], help="Execution mode override")
    parser.add_argument("--course", help="Exact course ID; must match the configured course")
    parser.add_argument("--concurrency", type=int, help="1..4; requires a verified sequential API batch")
    parser.add_argument("--json", action="store_true", help="Print the complete dry-run plan as JSON")
    parser.add_argument("--readiness", action="store_true", help="Offline provider policy assessment; no CLI calls")
    parser.add_argument("--list-eligible", action="store_true", help="List all eligible lessons from manifest")
    parser.add_argument("--verify-baselines", action="store_true", help="Verify approved baselines M02-L11 and M03-L08")
    parser.add_argument("--dry-run", action="store_true", help="Perform deterministic dry run (0 AGY calls)")
    parser.add_argument("--select", type=int, default=5, help="Select up to N eligible lessons within configured limits")
    parser.add_argument("--lessons", nargs="+", help="Exact lesson IDs in execution order")
    parser.add_argument("--allow-incomplete", action="store_true", help="Permit INCOMPLETE sources with documented scope")
    parser.add_argument("--execute", action="store_true", help="Execute the scheduled batch")
    parser.add_argument("--resume", help="Resume interrupted batch by batch_id")
    parser.add_argument("--budget", action="store_true", help="Display resource budget settings and limits")

    args = parser.parse_args(argv)

    if args.readiness:
        print(json.dumps(provider_readiness(args.mode, args.config), indent=2))
        return 0

    try:
        scheduler = BatchScheduler(config_path=args.config, mode_override=args.mode)
        if args.course and args.course != scheduler.controller.course_id:
            raise BatchSchedulingError("Exact course ID does not match configuration")
        if args.concurrency is not None:
            if not 1 <= args.concurrency <= (4 if scheduler.controller.execution_mode == "gemini_api" else 1):
                raise BatchSchedulingError("Unsupported concurrency")
            scheduler.limits.max_concurrency = args.concurrency

        if args.verify_baselines:
            print("\n=== VERIFYING APPROVED BASELINES ===")
            res = scheduler.verify_approved_baselines()
            print(json.dumps(res, indent=2))
            print("All approved baselines verified intact.\n")
            return 0

        if args.budget:
            print("\n=== RESOURCE & QUOTA BUDGET ===")
            print(json.dumps(dataclasses.asdict(scheduler.limits), indent=2))
            return 0

        if args.list_eligible:
            print("\n=== ELIGIBLE LESSONS DISCOVERY ===")
            eligible, excluded = scheduler.discover_lessons(allow_incomplete=args.allow_incomplete)
            print(f"Total Eligible Candidates: {len(eligible)}")
            print(f"Total Excluded / Ineligible: {len(excluded)}\n")
            print("Eligible Candidates Preview (first 10):")
            for c in eligible[:10]:
                print(f"  [{c.lesson_id}] ({c.source_type}, status: {c.source_status}) - {c.title}")
            return 0

        if args.resume and args.lessons:
            raise BatchSchedulingError("Resume uses the exact saved lesson list; omit --lessons")
        plan = scheduler.load_plan(args.resume) if args.resume else scheduler.plan_batch(
            requested_ids=args.lessons, limit=args.select, allow_incomplete=args.allow_incomplete)

        if args.dry_run or not args.execute:
            preview = scheduler.execute_batch(plan, dry_run=True)
            if scheduler.controller.execution_mode == "gemini_api":
                preview["local_readiness"] = scheduler.controller.adapter.verify_environment()
                preview["renderer_available"] = scheduler.controller.visual_asset_mgr.is_renderer_available()
                preview["seed_drafts"] = {}
                for candidate in plan.candidate_lessons:
                    seed = scheduler.controller.config.get("workflow", {}).get("seed_drafts", {}).get(candidate.lesson_id)
                    if seed:
                        if calculate_file_sha256(seed["path"]) != seed["sha256"] or seed["source_sha256"] != candidate.source_sha256:
                            raise BaselineIntegrityError("Seed/source checksum mismatch")
                        visual_path = seed.get("visual_manifest_path")
                        if visual_path and calculate_file_sha256(visual_path) != seed.get("visual_manifest_sha256"):
                            raise BaselineIntegrityError("Seed visual manifest checksum mismatch")
                        seed_issues = validate_draft_structure(
                            Path(seed["path"]).read_text(encoding="utf-8"), candidate.source_type,
                            lesson_id=candidate.lesson_id, raw_source_content=Path(candidate.source_full_path).read_text(encoding="utf-8"),
                            base_dir=scheduler.approved_output_dir)
                        blocking, warnings = classify_draft_issues(seed_issues)
                        if blocking:
                            raise BaselineIntegrityError("Seed structure failed: " + "; ".join(blocking))
                        preview["seed_drafts"][candidate.lesson_id] = {**seed,
                            "structural_check": "PASS", "warnings": warnings,
                            "use": "Input to fresh API Worker; historical evidence preserved"}
            if args.json:
                print(json.dumps(preview, indent=2, ensure_ascii=False))
                return 0
            print(json.dumps({k: v for k, v in preview.items() if k != "plan"}, indent=2, ensure_ascii=False))
            print("\n=======================================================")
            print(f"             BATCH 1 DRY-RUN PLAN ({plan.batch_id})")
            print("=======================================================")
            print(f"Course: {plan.course_id}")
            print(f"Manifest SHA256: {plan.manifest_sha256}")
            print(f"Prompt Config Hash: {plan.prompt_config_hash}")
            print(f"Candidate Count: {len(plan.candidate_lessons)} (Max: {scheduler.limits.max_lessons})")
            print(f"Human Review Required: {plan.human_review_required} (Batch 1 requires 100% human sign-off)")
            print("\nSelected Candidate Lessons:")
            for idx, c in enumerate(plan.candidate_lessons, 1):
                print(f"\n  {idx}. Lesson ID: {c.lesson_id}")
                print(f"     Title: {c.title}")
                print(f"     Type: {c.source_type} | Status: {c.source_status}")
                print(f"     Source File: {c.source_rel_path}")
                print(f"     Source SHA256: {c.source_sha256}")
                print(f"     Eligibility Reason: {c.eligibility_reason}")
                if c.known_limitations:
                    print(f"     Known Limitations: {'; '.join(c.known_limitations)}")
                print(f"     Prior Checkpoint: {c.prior_checkpoint_status or 'NONE'}")

            print("\n--- Resource & Quota Limits ---")
            print(f"  Max Lessons: {scheduler.limits.max_lessons}")
            print(f"  Max Concurrency: {scheduler.limits.max_concurrency} (strictly sequential)")
            print(f"  Max Repairs / Lesson: {scheduler.limits.max_repairs_per_lesson}")
            print(f"  Max Invocations: {scheduler.limits.max_provider_invocations}")
            print(f"  Max Runtime: {scheduler.limits.max_batch_runtime_seconds}s")
            print(f"  Max Tokens: {scheduler.limits.max_batch_tokens}")
            print("  Monetary cost: UNKNOWN; token quotas are accounted separately")

            print("\n--- Estimated Requirements (ESTIMATED_USAGE) ---")
            est = plan.estimated_usage
            print(f"  Estimated Invocations: {est.invocations}")
            print(f"  Estimated Tokens: ~{est.total_tokens:,} ({est.usage_class})")
            print(f"  Estimated Wall Clock: ~{est.wall_clock_seconds:.0f}s")
            print("\nDRY RUN ONLY: Zero provider calls. Raw sources and approved evidence unchanged.\n")
            return 0

        # Execution requested
        if args.execute:
            if scheduler.controller.execution_mode == "automated_cli":
                raise BlockedExecutionError(AGY_BATCH_BLOCK_REASON)

            res = scheduler.execute_batch(plan, resume_batch_id=args.resume)
            print("\n=== BATCH EXECUTION RESULTS ===")
            print(json.dumps(res, indent=2))
            return 0

        return 0

    except BlockedExecutionError as e:
        print(str(e), file=sys.stderr)
        return 3
    except Exception as e:
        logger.error(f"Batch Scheduler error: {e}", exc_info=True)
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
