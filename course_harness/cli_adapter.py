"""CLI Adapter for Google Antigravity (AGY) CLI.

Enforces model pinning (gemini-3.8-flash-high), fresh session isolation,
redaction of signed URLs and tokens, and dual execution modes:
  1. automated_cli (subprocess execution with safety checks)
  2. manual_cli_handoff (prepared prompts + CLI invocation guidance)
  3. mock (deterministic testing mode)
"""

import hashlib
import json
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import time
import uuid
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("course_harness.cli_adapter")

# Pinned model configuration
EXPECTED_MODEL = "gemini-3.8-flash-high"
EXPECTED_EFFORT = "high"

# Regex for redacting signed URL parameters
SIGNED_URL_QUERY_RE = re.compile(
    r'(https?://[^\s)"]+?\?)([^)\s"]+)',
    re.IGNORECASE
)
SENSITIVE_PARAM_RE = re.compile(
    r'(Expires|Signature|Key-Pair-Id|X-Amz-[A-Za-z0-9_-]+|token|access_token|expiry|hmac|auth)=([^&\s)"]+)',
    re.IGNORECASE
)


def redact_signed_urls(text: str) -> str:
    """Redacts query authentication tokens from signed media URLs in logs and prompts."""
    if not text:
        return text

    def _redact_query(match: re.Match) -> str:
        base_url = match.group(1)
        query = match.group(2)
        # Redact specific sensitive params
        redacted_query = SENSITIVE_PARAM_RE.sub(r'\1=[REDACTED]', query)
        return f"{base_url}{redacted_query}"

    return SIGNED_URL_QUERY_RE.sub(_redact_query, text)


class ModelUnavailableError(Exception):
    """Raised when the requested pinned model is unavailable in AGY CLI."""
    pass


class CliExecutionError(Exception):
    """Raised when the AGY CLI process fails during execution."""
    pass


class AgyAdapter:
    """Adapter for invoking Gemini 3.8 Flash High through AGY CLI."""

    def __init__(
        self,
        mode: str = "automated_cli",
        agy_binary: Optional[str] = None,
        timeout_seconds: int = 180,
        model: str = EXPECTED_MODEL,
        effort: str = EXPECTED_EFFORT,
        evidence_dir: Optional[str] = None,
        session_dir: Optional[str] = None,
    ):
        self.mode = mode
        self.model = model
        self.effort = effort
        env_timeout = os.environ.get("AGY_TIMEOUT_SECONDS")
        if env_timeout:
            try:
                timeout_seconds = int(env_timeout)
            except ValueError:
                pass
        self.timeout_seconds = timeout_seconds
        self.evidence_dir = evidence_dir or "generated_course/Agile_Project_Management/evidence"
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.session_dir = session_dir

        self.resolved_binary = self._resolve_agy_binary(agy_binary)
        self.verified_version: Optional[str] = None
        self.verified_model: Optional[str] = None
        self.last_model_verified: Optional[str] = None

    def _resolve_agy_binary(self, preferred_path: Optional[str]) -> Optional[str]:
        """Resolves the path to the agy binary."""
        if preferred_path and os.path.isfile(preferred_path) and os.access(preferred_path, os.X_OK):
            return preferred_path
        
        # Check standard user local bin
        user_local = os.path.expanduser("~/.local/bin/agy")
        if os.path.isfile(user_local) and os.access(user_local, os.X_OK):
            return user_local

        # Check system PATH
        which_path = shutil.which("agy")
        if which_path:
            return which_path

        return None

    def resolve_session_model(self, conversation_id: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Resolves model identity directly from AGY CLI session execution artifacts.
        
        Inspects:
        1. Conversation SQLite DB (gen_metadata or executor_metadata table for model protobuf tag)
        2. Session transcript log (system setting change preamble in Step 0)
        
        Returns:
            Tuple of (model_identifier, evidence_dict) or (None, None) if not resolvable.
        """
        if not conversation_id or conversation_id.startswith("fresh-"):
            return None, None

        candidate_dirs = []
        if self.session_dir and os.path.isdir(self.session_dir):
            candidate_dirs.append(self.session_dir)
        for def_dir in ["~/.gemini/antigravity-cli", "~/.gemini/antigravity"]:
            exp = os.path.expanduser(def_dir)
            if os.path.isdir(exp) and exp not in candidate_dirs:
                candidate_dirs.append(exp)

        KNOWN_MODELS = [
            ("gemini-3.8-flash-high", "gemini 3.8 flash (high)"),
            ("gemini-3.8-flash-medium", "gemini 3.8 flash (medium)"),
            ("gemini-3.8-flash-low", "gemini 3.8 flash (low)"),
            ("claude-sonnet-4-6", "claude sonnet 4.6 (thinking)"),
            ("claude-opus-4-6-thinking", "claude opus 4.6 (thinking)"),
            ("gpt-oss-120b-medium", "gpt-oss 120b (medium)"),
        ]

        # 1. Inspect conversation SQLite DB (authoritative execution metadata)
        for base in candidate_dirs:
            db_path = os.path.join(base, "conversations", f"{conversation_id}.db")
            if os.path.isfile(db_path):
                try:
                    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                    cur = conn.cursor()
                    cur.execute("SELECT data FROM gen_metadata WHERE idx=0")
                    row = cur.fetchone()
                    if not row or not row[0]:
                        cur.execute("SELECT data FROM executor_metadata WHERE idx=0")
                        row = cur.fetchone()
                    conn.close()

                    if row and row[0]:
                        data = row[0]
                        # Protobuf tag 28 wire type 2: b"\xe2\x01" followed by length byte
                        tag_pos = data.find(b"\xe2\x01")
                        if tag_pos != -1 and tag_pos + 2 < len(data):
                            length = data[tag_pos + 2]
                            if tag_pos + 3 + length <= len(data):
                                model_bytes = data[tag_pos + 3 : tag_pos + 3 + length]
                                model_str = model_bytes.decode("utf-8", errors="ignore").strip()
                                if model_str and re.match(r"^[a-zA-Z0-9_.-]+$", model_str):
                                    evidence = {
                                        "source": "sqlite_gen_metadata",
                                        "conversation_id": conversation_id,
                                        "db_path": db_path,
                                        "model_resolved": model_str,
                                        "raw_snippet_hex": data[tag_pos : tag_pos + 3 + length].hex(),
                                    }
                                    return model_str, evidence

                        # Check known models in binary data
                        data_lower = data.lower()
                        for mid, disp in KNOWN_MODELS:
                            if mid.encode("utf-8") in data or disp.encode("utf-8") in data_lower:
                                evidence = {
                                    "source": "sqlite_gen_metadata_known_model",
                                    "conversation_id": conversation_id,
                                    "db_path": db_path,
                                    "model_resolved": mid,
                                }
                                return mid, evidence
                except Exception as e:
                    logger.debug(f"Failed to inspect SQLite session DB at {db_path}: {e}")

        # 2. Inspect session transcript step 0 system metadata
        display_map = {disp: mid for mid, disp in KNOWN_MODELS}
        for base in candidate_dirs:
            for t_name in ["transcript_full.jsonl", "transcript.jsonl"]:
                t_path = os.path.join(base, "brain", conversation_id, ".system_generated", "logs", t_name)
                if os.path.isfile(t_path):
                    try:
                        with open(t_path, "r", encoding="utf-8") as f:
                            first_line = f.readline()
                        step0 = json.loads(first_line)
                        content = step0.get("content", "")
                        m = re.search(
                            r"The user changed setting `Model Selection` from None to ([^\n.]+?)\. No need to comment",
                            content,
                        )
                        if m:
                            display_name = m.group(1).strip()
                            resolved = display_map.get(display_name.lower())
                            if not resolved and display_name.lower().startswith("gemini"):
                                resolved = display_name.lower().replace(" ", "-")
                            if resolved:
                                evidence = {
                                    "source": "transcript_system_setting",
                                    "conversation_id": conversation_id,
                                    "transcript_path": t_path,
                                    "display_name": display_name,
                                    "model_resolved": resolved,
                                }
                                return resolved, evidence
                    except Exception as e:
                        logger.debug(f"Failed to inspect transcript at {t_path}: {e}")

        return None, None

    def verify_environment(self) -> Dict[str, Any]:
        """Verifies AGY CLI installation and pinned model availability."""
        # Enforce model pinning first
        if self.model != EXPECTED_MODEL:
            raise ModelUnavailableError(
                f"BLOCKED_MODEL_UNAVAILABLE: Model pinning violation: requested '{self.model}', expected '{EXPECTED_MODEL}'"
            )
        if self.effort != EXPECTED_EFFORT:
            raise ModelUnavailableError("BLOCKED_MODEL_UNAVAILABLE: AGY effort must be high")

        if self.mode == "mock":
            return {
                "status": "VERIFIED_MOCK",
                "binary": "mock",
                "version": "1.4.5-mock",
                "model_resolved": EXPECTED_MODEL,
                "effort_resolved": EXPECTED_EFFORT,
            }

        if not self.resolved_binary:
            raise ModelUnavailableError(
                "BLOCKED_MODEL_UNAVAILABLE: agy binary not found in PATH or ~/.local/bin/agy"
            )

        # 1. Check version
        try:
            res = subprocess.run(
                [self.resolved_binary, "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            )
            self.verified_version = res.stdout.strip()
        except Exception as e:
            raise ModelUnavailableError(f"BLOCKED_MODEL_UNAVAILABLE: Failed to run agy --version: {e}")

        # 2. Check models list
        try:
            res = subprocess.run(
                [self.resolved_binary, "models"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            output = res.stdout
            if EXPECTED_MODEL not in output:
                raise ModelUnavailableError(
                    f"BLOCKED_MODEL_UNAVAILABLE: Pinned model '{EXPECTED_MODEL}' not found in 'agy models' output"
                )
            self.verified_model = EXPECTED_MODEL
        except subprocess.TimeoutExpired:
            # If models command times out, check if model is directly runnable
            logger.warning("agy models timed out, will verify via test prompt")
        except Exception as e:
            if not isinstance(e, ModelUnavailableError):
                raise ModelUnavailableError(f"BLOCKED_MODEL_UNAVAILABLE: agy models inspection failed: {e}")
            raise

        # 3. Model pinning verification
        if self.model != EXPECTED_MODEL:
            raise ModelUnavailableError(
                f"BLOCKED_MODEL_UNAVAILABLE: Model pinning violation: requested '{self.model}', expected '{EXPECTED_MODEL}'"
            )

        return {
            "status": "VERIFIED",
            "binary": self.resolved_binary,
            "version": self.verified_version,
            "model_resolved": self.verified_model or EXPECTED_MODEL,
            "effort_resolved": self.effort,
        }

    def invoke(
        self,
        prompt: str,
        role: str,
        lesson_id: str,
        fresh_session: bool = True,
        output_format: str = "text",
        step_attempt: int = 1,
        invocation_id: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Invokes the model for a specific role (worker, auditor, repair).
        
        Returns:
            Tuple of (response_text, execution_metadata)
        """
        if self.model != EXPECTED_MODEL:
            raise ModelUnavailableError(
                f"BLOCKED_MODEL_UNAVAILABLE: Model '{self.model}' is not permitted. Only '{EXPECTED_MODEL}' is allowed."
            )
        if self.effort != EXPECTED_EFFORT:
            raise ModelUnavailableError("BLOCKED_MODEL_UNAVAILABLE: AGY effort must be high")
        if not fresh_session:
            raise CliExecutionError("FRESH_SESSION_REQUIRED: Worker, Auditor and Repair use separate AGY processes")
        if role not in {"worker", "auditor", "repair"} or not re.fullmatch(r"[A-Za-z0-9_-]+", lesson_id):
            raise ValueError("Invalid role or lesson ID")

        if self.mode == "automated_cli":
            invocation_id = invocation_id or f"inv-{role}-{lesson_id}-att{step_attempt}-{uuid.uuid4().hex[:12]}"
            if not re.fullmatch(r"[A-Za-z0-9_-]+", invocation_id):
                raise ValueError("Invalid invocation ID")

        # Sanitize prompt before logging/persisting
        safe_prompt = redact_signed_urls(prompt)

        # Save prompt artifact in evidence
        prompt_filename = f"{invocation_id}.prompt.md" if self.mode == "automated_cli" else f"prompt_{role}_{lesson_id}_att{step_attempt}.md"
        prompt_path = os.path.join(self.evidence_dir, prompt_filename)
        with open(prompt_path, "x" if self.mode == "automated_cli" else "w", encoding="utf-8") as f:
            f.write(safe_prompt)

        if self.mode == "mock":
            return self._invoke_mock(role, lesson_id, prompt, invocation_id=invocation_id)

        if self.mode == "manual_cli_handoff":
            return self._invoke_manual_handoff(
                prompt_path, role, lesson_id, step_attempt, invocation_id=invocation_id
            )

        if self.mode == "automated_cli":
            return self._invoke_automated(
                prompt, prompt_path, role, lesson_id, output_format, step_attempt, invocation_id=invocation_id
            )

        raise ValueError(f"Unknown execution mode: {self.mode}")

    def _invoke_automated(
        self,
        prompt: str,
        prompt_path: str,
        role: str,
        lesson_id: str,
        output_format: str,
        step_attempt: int,
        invocation_id: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Executes AGY CLI non-interactively via subprocess."""
        if not self.resolved_binary:
            raise ModelUnavailableError("BLOCKED_MODEL_UNAVAILABLE: agy binary not available")

        # Sanitize prompt so process args in ps don't contain raw signed tokens
        safe_prompt = redact_signed_urls(prompt)
        inv_id = invocation_id or f"inv-{role}-{lesson_id}-att{step_attempt}-{uuid.uuid4().hex[:12]}"
        if not re.fullmatch(r"[A-Za-z0-9_-]+", inv_id):
            raise ValueError("Invalid invocation ID")
        raw_path = os.path.join(self.evidence_dir, f"{inv_id}.raw.json")
        if os.path.exists(raw_path):
            raise CliExecutionError("REUSED_INVOCATION_ID: Existing raw AGY evidence must not be overwritten")

        cmd = [
            self.resolved_binary,
            "-p",
            safe_prompt,
            "--model",
            self.model,
            "--effort",
            self.effort,
            "--disable-slash-commands",
            "--output-format",
            "json",  # Always request json envelope to capture metadata reliably
        ]

        start_time = time.time()
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.timeout_seconds,
            )
            duration = time.time() - start_time
            raw_output = res.stdout
            # Preserve the original transport response before validating its envelope.
            with open(raw_path, "x", encoding="utf-8") as raw_file:
                os.chmod(raw_path, 0o600)
                raw_file.write(raw_output)
            raw_hash = hashlib.sha256(raw_output.encode("utf-8")).hexdigest()

            # Strictly parse AGY transport JSON envelope for all roles (Worker, Auditor, Repair)
            try:
                envelope = json.loads(raw_output)
            except (json.JSONDecodeError, TypeError) as e:
                raise CliExecutionError(
                    f"MALFORMED_AGY_JSON: Failed to parse AGY JSON envelope: {e}"
                ) from e

            if not isinstance(envelope, dict):
                raise CliExecutionError(
                    "MALFORMED_AGY_JSON: AGY output is not a JSON object"
                )

            # 1. Check for error fields in JSON envelope
            if "error" in envelope and envelope["error"]:
                err_val = json.dumps(envelope["error"]) if isinstance(envelope["error"], (dict, list)) else str(envelope["error"])
                safe_err = redact_signed_urls(err_val)
                raise CliExecutionError(f"AGY reported error in JSON envelope: {safe_err}")

            # 2. Check terminal status
            if "status" not in envelope or not envelope["status"]:
                raise CliExecutionError(
                    "MALFORMED_AGY_JSON: Missing or empty 'status' in AGY envelope"
                )

            st_norm = str(envelope["status"]).strip().upper()
            if st_norm in {"ERROR", "WAITING", "INTERRUPTED", "FAILED", "CANCELLED", "TIMEOUT"}:
                raise CliExecutionError(
                    f"AGY returned non-terminal / error status: '{envelope['status']}'"
                )
            if st_norm not in {"SUCCESS", "COMPLETED", "DONE", "OK"}:
                raise CliExecutionError(
                    f"AGY returned unsupported/unknown status: '{envelope['status']}'"
                )

            # 3. Check response payload
            if "response" not in envelope or envelope["response"] is None:
                raise CliExecutionError(
                    "MALFORMED_AGY_JSON: Missing 'response' field in AGY envelope"
                )

            if not isinstance(envelope["response"], str):
                raise CliExecutionError("MALFORMED_AGY_JSON: 'response' must be text")
            response_text = envelope["response"]
            if not response_text.strip():
                raise CliExecutionError(
                    "MALFORMED_AGY_JSON: Empty 'response' text in AGY envelope"
                )

            conversation_id = envelope.get("conversation_id") or None
            usage = envelope.get("usage")

            # 4. Model verification: inspect envelope first, then session artifacts
            model_reported = envelope.get("model")
            session_ev = None
            if model_reported is not None and str(model_reported).strip():
                model_reported = str(model_reported).strip()
            else:
                resolved_model, session_ev = self.resolve_session_model(conversation_id)
                if resolved_model:
                    model_reported = resolved_model

            if model_reported is not None and str(model_reported).strip():
                if model_reported != self.model:
                    self.last_model_verified = "MISMATCH"
                    raise ModelUnavailableError(
                        f"BLOCKED_MODEL_UNAVAILABLE: AGY model mismatch (expected '{self.model}', got '{model_reported}')"
                    )
                model_verified = "VERIFIED"
            else:
                model_reported = None
                model_verified = "NOT_VERIFIED"

            self.last_model_verified = model_verified

            metadata = {
                "mode": "automated_cli",
                "execution_mode": "automated_cli",
                "evidence_class": "REAL_AGY_VERIFIED" if model_verified == "VERIFIED" else "MANUAL_UNVERIFIED",
                "provider": "agy",
                "terminal_status": st_norm,
                "role": role,
                "lesson_id": lesson_id,
                "attempt": step_attempt,
                "invocation_id": inv_id,
                "model_requested": self.model,
                "model_reported": model_reported,
                "model_verified": model_verified,
                "model": self.model,
                "effort": self.effort,
                "conversation_id": conversation_id,
                "fresh_session": True,
                "duration_seconds": round(duration, 3),
                "usage": usage,
                "request_id": envelope.get("request_id"),
                "response_id": envelope.get("response_id"),
                "prompt_path": prompt_path,
                "prompt_sha256": hashlib.sha256(safe_prompt.encode("utf-8")).hexdigest(),
                "raw_response_path": raw_path,
                "raw_response_sha256": raw_hash,
                "response_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start_time)),
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            if session_ev:
                metadata["model_verification_evidence"] = session_ev

            if role == "auditor":
                metadata["auditor_boundary"] = {
                    "fresh_session": True,
                    "write_boundary_status": "PROMPT_AND_CONTROLLER_ENFORCED_ONLY",
                    "os_filesystem_sandbox": "NOT_VERIFIED",
                    "verification_evidence": (
                        "NOT_VERIFIED (No OS-level sandbox or filesystem write restriction "
                        "demonstrated in AGY CLI invocation; read-only boundary is maintained "
                        "by prompt instructions and controller read-only contract.)"
                    ),
                }

            # Save execution evidence
            evidence_file = os.path.join(
                self.evidence_dir, f"{inv_id}.json"
            )
            metadata["evidence_path"] = evidence_file
            with open(evidence_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            return response_text, metadata

        except subprocess.TimeoutExpired as e:
            raise CliExecutionError(
                f"AGY CLI timed out after {self.timeout_seconds} seconds for {role} {lesson_id}"
            ) from e
        except subprocess.CalledProcessError as e:
            safe_err = redact_signed_urls(e.stderr or "")
            raise CliExecutionError(
                f"AGY CLI failed with exit code {e.returncode}: {safe_err}"
            ) from e

    def _invoke_manual_handoff(
        self,
        prompt_path: str,
        role: str,
        lesson_id: str,
        step_attempt: int,
        invocation_id: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Prepares handoff instructions and checks for user-provided output with strict metadata binding.
        
        Note: UUID/mtime/consumed controls provide basic session hygiene and freshness checks
        against accidental file reuse; they do not represent cryptographically verified operator
        identity or strong cryptographic output-request authenticity.
        """
        output_filename = f"output_{role}_{lesson_id}_att{step_attempt}.txt"
        output_path = os.path.join(self.evidence_dir, output_filename)
        instructions_file = os.path.join(
            self.evidence_dir, f"handoff_{role}_{lesson_id}_att{step_attempt}.md"
        )
        handoff_meta_file = os.path.join(
            self.evidence_dir, f"handoff_{role}_{lesson_id}_att{step_attempt}.json"
        )

        def _calc_sha(fpath: str) -> Optional[str]:
            if not os.path.exists(fpath):
                return None
            h = hashlib.sha256()
            with open(fpath, "rb") as bf:
                while chunk := bf.read(65536):
                    h.update(chunk)
            return h.hexdigest()

        prompt_sha256 = _calc_sha(prompt_path)
        current_time = time.time()

        if os.path.exists(handoff_meta_file):
            try:
                with open(handoff_meta_file, "r", encoding="utf-8") as f:
                    h_meta = json.load(f)
            except Exception:
                h_meta = {}
        else:
            h_meta = {}

        request_id = h_meta.get("request_id")
        if not request_id:
            request_id = f"req-{lesson_id}-{role}-att{step_attempt}-{uuid.uuid4().hex[:12]}"
            h_meta = {
                "request_id": request_id,
                "lesson_id": lesson_id,
                "role": role,
                "attempt": step_attempt,
                "prompt_path": prompt_path,
                "prompt_sha256": prompt_sha256,
                "model_requested": self.model,
                "effort": self.effort,
                "requested_at": current_time,
                "consumed": False,
                "consumed_at": None,
                "consumed_output_sha256": None,
            }
            with open(handoff_meta_file, "w", encoding="utf-8") as f:
                json.dump(h_meta, f, indent=2)

        # Check prompt hash consistency
        if h_meta.get("prompt_sha256") and prompt_sha256 and h_meta.get("prompt_sha256") != prompt_sha256:
            raise CliExecutionError(
                f"STALE_HANDOFF_PROMPT: Prompt file has changed since handoff was prepared. "
                f"Expected prompt sha {h_meta.get('prompt_sha256')}, got {prompt_sha256}."
            )

        # Reject reused manual handoff
        if h_meta.get("consumed") is True:
            raise CliExecutionError(
                f"REUSED_MANUAL_OUTPUT: Handoff request '{request_id}' has already been consumed. "
                "Reusing previous manual output is prohibited."
            )

        cli_command = (
            f'{self.resolved_binary or "agy"} -p "$(cat {prompt_path})" '
            f'--model {self.model} --effort {self.effort} '
            f'--disable-slash-commands > {output_path}'
        )

        handoff_content = (
            f"# MANUAL CLI HANDOFF INSTRUCTION\n\n"
            f"- **Request ID:** `{request_id}`\n"
            f"- **Role:** {role}\n"
            f"- **Lesson ID:** {lesson_id}\n"
            f"- **Attempt:** {step_attempt}\n"
            f"- **Prompt SHA256:** `{prompt_sha256}`\n"
            f"- **Model Requested:** {self.model} (effort: {self.effort})\n"
            f"- **Prompt File:** `{prompt_path}`\n"
            f"- **Target Output File:** `{output_path}`\n\n"
            f"### Command to run:\n"
            f"```bash\n{cli_command}\n```\n\n"
            f"After running, the Controller will automatically load and validate `{output_path}`.\n"
        )

        with open(instructions_file, "w", encoding="utf-8") as f:
            f.write(handoff_content)

        # Check if output exists and is fresh
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            output_mtime = os.path.getmtime(output_path)
            req_time = h_meta.get("requested_at", current_time)

            # Strict freshness check: output must not predate handoff request
            if output_mtime < req_time - 0.05:
                raise CliExecutionError(
                    f"STALE_MANUAL_OUTPUT: Output file '{output_path}' predates handoff request "
                    f"(mtime: {output_mtime} < requested_at: {req_time}). Run the command to generate fresh output."
                )

            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                raise CliExecutionError(
                    f"EMPTY_MANUAL_OUTPUT: Output file '{output_path}' contains only whitespace."
                )

            output_sha256 = _calc_sha(output_path)

            # Mark handoff as consumed to prevent reuse
            h_meta["consumed"] = True
            h_meta["consumed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            h_meta["consumed_output_sha256"] = output_sha256
            with open(handoff_meta_file, "w", encoding="utf-8") as f:
                json.dump(h_meta, f, indent=2)

            metadata = {
                "mode": "manual_cli_handoff",
                "execution_mode": "manual_cli_handoff",
                "evidence_class": "MANUAL_UNVERIFIED",
                "provider": "manual",
                "terminal_status": "MANUAL_SUCCESS",
                "role": role,
                "lesson_id": lesson_id,
                "attempt": step_attempt,
                "invocation_id": invocation_id or request_id,
                "request_id": request_id,
                "prompt_sha256": prompt_sha256,
                "output_sha256": output_sha256,
                "model_requested": self.model,
                "model_reported": None,
                "model_verified": "NOT_VERIFIED",
                "model": self.model,
                "effort": self.effort,
                "conversation_id": f"manual-{request_id}",
                "prompt_path": prompt_path,
                "output_path": output_path,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

            if role == "auditor":
                metadata["auditor_boundary"] = {
                    "fresh_session": True,
                    "write_boundary_status": "MANUAL_OPERATOR_BOUNDARY",
                    "os_filesystem_sandbox": "NOT_VERIFIED",
                    "verification_evidence": (
                        "NOT_VERIFIED (Manual operator handoff; no OS sandbox enforced)"
                    ),
                }

            self.last_model_verified = "NOT_VERIFIED"
            return content, metadata

        raise CliExecutionError(
            f"MANUAL_HANDOFF_REQUIRED: Prompt prepared at '{prompt_path}'. "
            f"Request ID: {request_id}. "
            f"Run the command indicated in '{instructions_file}' and write output to '{output_path}'."
        )

    def _invoke_mock(
        self, role: str, lesson_id: str, prompt: str, invocation_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Mock invocation for deterministic unit tests without calling external CLI."""
        inv_id = invocation_id or f"inv-{role}-{lesson_id}-att1-{uuid.uuid4().hex[:12]}"
        metadata = {
            "mode": "mock",
            "execution_mode": "mock",
            "evidence_class": "MOCK_SIMULATED",
            "provider": "mock",
            "terminal_status": "SIMULATED",
            "role": role,
            "lesson_id": lesson_id,
            "attempt": 1,
            "invocation_id": inv_id,
            "model_requested": self.model,
            "model_reported": "mock",
            "model_verified": "NOT_APPLICABLE",
            "model": self.model,
            "effort": self.effort,
            "conversation_id": f"mock-conv-{lesson_id}",
            "duration_seconds": 0.01,
            "usage": {"total_tokens": 100},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.last_model_verified = "NOT_APPLICABLE"

        if role == "auditor":
            metadata["auditor_boundary"] = {
                "fresh_session": True,
                "write_boundary_status": "PROMPT_AND_CONTROLLER_ENFORCED_ONLY",
                "os_filesystem_sandbox": "NOT_VERIFIED",
                "verification_evidence": (
                    "NOT_VERIFIED (No OS-level sandbox or filesystem write restriction "
                    "demonstrated in AGY CLI invocation; read-only boundary is maintained "
                    "by prompt instructions and controller read-only contract.)"
                ),
            }

        if role == "worker":
            response = (
                f"# Bài học Mock {lesson_id}\n\n"
                f"## 1. Mục tiêu bài học (Learning Objectives)\n- Nắm vững kiến thức mock.\n\n"
                f"<!-- FIGURE_START: F01 -->\n"
                f"#### Hình F01: Sơ đồ minh họa tiến trình học tập {lesson_id}\n\n"
                f"```mermaid\n"
                f"graph TD\n"
                f"    A[Mục tiêu bài học] --> B[Nội dung lý thuyết]\n"
                f"    B --> C[Tóm tắt cốt lõi]\n"
                f"```\n\n"
                f"*Hình F01: Sơ đồ minh họa tiến trình học tập tổng quan của bài học.*\n\n"
                f"> **Mô tả trực quan (Alt text):** Sơ đồ khối 3 bước từ mục tiêu đến lý thuyết và tóm tắt.\n"
                f"> **Mục tiêu giáo dục:** Cung cấp bức tranh toàn cảnh về tiến trình bài học.\n"
                f"> **Xuất xứ học liệu (Provenance):** `PEDAGOGICAL_RECONSTRUCTION` [00:01].\n"
                f"<!-- FIGURE_END: F01 -->\n\n"
                f"## 2. Kiến thức nền tảng (Context)\n- Agile Scrum context.\n\n"
                f"## 3. Nội dung lý thuyết trọng tâm\n- Chi tiết lý thuyết mock.\n\n"
                f"## 5. Bảng thuật ngữ chuyên ngành Anh - Việt\n| Term | Nghĩa | Ghi chú |\n| Agile | Linh hoạt | Phương pháp |\n\n"
                f"## 6. Tóm tắt cốt lõi\n- Điểm chính 1.\n\n"
                f"## 8. Nguồn đối chiếu\n- Source reference locator.\n"
            )
        elif role == "auditor":
            response = json.dumps(
                {
                    "lesson_id": lesson_id,
                    "verdict": "PASS",
                    "quality_rubric_version": "2.0-visual-first",
                    "content_quality_accepted": True,
                    "quality_score": 100.0,
                    "summary": "Mock audit passed with flying colors.",
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
                    "limitations": ["Mock test environment"],
                },
                indent=2,
            )
        elif role == "repair":
            response = f"# Repaired Mock {lesson_id}\n\nFixed all findings cleanly."
        else:
            response = "MOCK_RESPONSE"

        return response, metadata
