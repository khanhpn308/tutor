"""Stateless Gemini Developer API calls with durable, unmodified response evidence."""

import hashlib
import json
import os
from pathlib import Path
import re
import time
import uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from course_harness.cli_adapter import redact_signed_urls

MODEL = "gemini-3.8-flash"
EVIDENCE_CLASS = "REAL_GEMINI_API_VERIFIED"


class GeminiApiError(RuntimeError):
    """A provider failure, distinct from an educational FAIL verdict."""


class ApiDisabledError(GeminiApiError):
    """The operator has not authorized the API provider."""


class ApiAuthenticationError(GeminiApiError):
    pass


class ApiBudgetError(GeminiApiError):
    pass


class ApiIntegrityError(GeminiApiError):
    pass


class ApiTransientError(GeminiApiError):
    pass


class ApiResponseError(GeminiApiError):
    pass


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, data):
    temporary = Path(str(path) + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def matches_model_version(model):
    return isinstance(model, str) and bool(re.fullmatch(re.escape(MODEL) + r"(?:-\d{3}|-\d{2}-\d{2}|-\d{4}-\d{2}-\d{2})?", model))


def verified_api_receipt(receipt):
    """Check provider identity and its original response, including on resume."""
    if not (
        receipt.get("execution_mode") == "gemini_api"
        and receipt.get("provider") == "google_gemini_api"
        and receipt.get("evidence_class") == EVIDENCE_CLASS
        and receipt.get("model_requested") == MODEL
        and receipt.get("thinking_level") == "high"
        and receipt.get("model_verified") == "VERIFIED"
    ):
        return False
    try:
        raw = Path(receipt["raw_response_path"]).read_text(encoding="utf-8")
        payload = json.loads(raw)
        return (
            sha256(raw) == receipt["raw_response_sha256"]
            and payload.get("modelVersion") == receipt.get("model_reported")
            and matches_model_version(payload.get("modelVersion"))
            and payload.get("responseId") == receipt.get("response_id")
            and payload.get("candidates", [{}])[0].get("finishReason") == "STOP"
        )
    except (OSError, KeyError, ValueError, IndexError, TypeError):
        return False


class GeminiApiAdapter:
    """Implements the Controller's invoke/verify_environment adapter contract."""

    mode = "gemini_api"
    model = MODEL
    effort = "high"

    def __init__(self, evidence_dir, schema_path, timeout_seconds=180,
                 max_retries=2, client=None):
        if timeout_seconds <= 0 or not 0 <= max_retries <= 5:
            raise ValueError("Positive timeout and 0..5 API retries required")
        self.evidence_dir = Path(evidence_dir) / "gemini_api"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        self.schema["required"] = list(dict.fromkeys(self.schema["required"] + [
            "dimension_scores", "quality_rubric_version", "quality_score", "content_quality_accepted", "audited_final_sha256"]))
        self.schema["properties"]["dimension_scores"]["required"] = [
            "SOURCE_FIDELITY", "CONTENT_COMPLETENESS", "PEDAGOGICAL_QUALITY", "VISUAL_PEDAGOGY",
            "TERMINOLOGY_CONSISTENCY", "SOURCE_TRACEABILITY", "CLARITY_ORGANIZATION", "FORMATTING"]
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.client = client
        self.last_model_verified = None
        self.before_attempt = None
        self.on_attempt = None

    def verify_environment(self):
        return {"status": "PROVIDER_DISABLED", "reason": "GEMINI_API_NOT_AUTHORIZED",
                "authentication": "NOT_CHECKED", "billing": "NOT_CHECKED",
                "model_requested": MODEL, "thinking_level": "high"}

    def _get_client(self):
        if self.client is None:
            raise ApiDisabledError("GEMINI_API_NOT_AUTHORIZED: Live API client creation is disabled")
        return self.client

    def close(self):
        if self.client is not None:
            self.client.close()

    def invoke(self, prompt, role, lesson_id, fresh_session=True, output_format="text",
               step_attempt=1, invocation_id=None):
        client = self._get_client()
        from google.genai import types
        import httpx

        if role not in ("worker", "auditor", "repair") or not fresh_session:
            raise ValueError("Only independent worker/auditor/repair requests are supported")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", lesson_id):
            raise ValueError("Unsafe lesson ID")
        inv_id = invocation_id or f"inv-{role}-{lesson_id}-{uuid.uuid4().hex}"
        if not re.fullmatch(r"[A-Za-z0-9_-]+", inv_id):
            raise ValueError("Unsafe invocation ID")
        prompt = redact_signed_urls(prompt)
        secret = os.environ.get("GEMINI_API_KEY")
        if secret:
            prompt = prompt.replace(secret, "[REDACTED]")
        prompt_path = self.evidence_dir / f"{inv_id}.prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        config = {"thinking_config": {"thinking_level": "HIGH"},
                  "should_return_http_response": True}
        if role == "auditor" or output_format == "json":
            config.update(response_mime_type="application/json", response_json_schema=self.schema)
        # Validate against the installed official SDK before making a request.
        config = types.GenerateContentConfig(**config)
        for retry in range(self.max_retries + 1):
            if self.before_attempt:
                self.before_attempt()
            start = time.monotonic()
            meta = {"mode": self.mode, "execution_mode": self.mode,
                    "provider": "google_gemini_api", "role": role, "lesson_id": lesson_id,
                    "invocation_id": inv_id, "step_attempt": step_attempt,
                    "api_attempt": retry + 1, "batch_id": getattr(self, "batch_id", None), "model_requested": MODEL,
                    "thinking_level": "high", "model_reported": None,
                    "model_verified": "NOT_VERIFIED", "evidence_class": "UNVERIFIED",
                    "started_at": utc_now(), "terminal_status": "STARTED",
                    "prompt_path": str(prompt_path), "prompt_sha256": sha256(prompt),
                    "usage": None, "monetary_cost": None, "currency": None}
            evidence_path = self.evidence_dir / f"{inv_id}.try{retry + 1}.json"
            write_json(evidence_path, meta)
            response = None
            error = None
            delay = min(2 ** retry, 30)
            try:
                # No chat history, previous response ID, tools, or Worker verdict are reused.
                response = client.models.generate_content(model=MODEL, contents=prompt, config=config)
            except Exception as exc:
                code = getattr(exc, "code", None)
                meta["http_status"] = code
                # Exception messages/URLs can contain keys. Persist only safe classifications.
                meta["error_type"] = type(exc).__name__
                if code in (401, 403):
                    error = ApiAuthenticationError("Gemini API authentication/permission failure")
                elif code == 402:
                    error = ApiBudgetError("Gemini API billing failure")
                elif code in (408, 429, 500, 502, 503, 504) or isinstance(exc, (TimeoutError, httpx.TransportError)):
                    error = ApiTransientError(f"Gemini transient failure (HTTP {code or 'transport'})")
                    headers = getattr(getattr(exc, "response", None), "headers", {}) or {}
                    try:
                        delay = max(delay, float(headers.get("retry-after", 0)))
                    except (ValueError, TypeError):
                        try:
                            retry_at = parsedate_to_datetime(headers["retry-after"])
                            delay = max(delay, (retry_at - datetime.now(timezone.utc)).total_seconds())
                        except (KeyError, ValueError, TypeError):
                            pass
                else:
                    error = ApiResponseError(f"Gemini API request failed (HTTP {code or 'unknown'})")
            try:
                if error is None:
                    transport = getattr(response, "sdk_http_response", None)
                    raw = getattr(transport, "body", None)
                    if not isinstance(raw, str):
                        raise ApiResponseError("Missing original Gemini response body")
                    raw_path = self.evidence_dir / f"{inv_id}.try{retry + 1}.raw.json"
                    raw_path.write_text(raw, encoding="utf-8")
                    meta.update(raw_response_path=str(raw_path), raw_response_sha256=sha256(raw))
                    headers = getattr(transport, "headers", {}) or {}
                    meta["request_id"] = headers.get("x-request-id") or headers.get("x-goog-request-id")
                    try:
                        payload = json.loads(raw)
                        parsed = types.GenerateContentResponse.model_validate(payload)
                    except (ValueError, TypeError):
                        raise ApiResponseError("Invalid Gemini response JSON") from None
                    usage = parsed.usage_metadata
                    if usage is not None:
                        meta["usage_metadata"] = usage.model_dump(mode="json", exclude_none=True)
                        meta["usage"] = {"input_tokens": usage.prompt_token_count,
                                         "output_tokens": usage.candidates_token_count,
                                         "thinking_tokens": usage.thoughts_token_count,
                                         "total_tokens": usage.total_token_count,
                                         "cached_input_tokens": usage.cached_content_token_count}
                    meta.update(response_id=parsed.response_id, model_reported=parsed.model_version,
                                provider_created_at=str(parsed.create_time) if parsed.create_time else None)
                    if not parsed.candidates or len(parsed.candidates) != 1:
                        raise ApiResponseError("Missing or ambiguous Gemini candidate")
                    candidate = parsed.candidates[0]
                    if candidate.finish_reason != types.FinishReason.STOP:
                        raise ApiResponseError("Gemini candidate did not finish with STOP")
                    text_parts = [p.text for p in ((candidate.content.parts or []) if candidate.content else [])
                                  if p.text and not p.thought]
                    result = "".join(text_parts)
                    if not result.strip():
                        raise ApiResponseError("Empty Gemini response text")
                    reported = parsed.model_version or ""
                    if not matches_model_version(reported):
                        raise ApiIntegrityError("Missing or mismatched Gemini model version")
                    self.last_model_verified = "VERIFIED"
                    meta.update(model_verified="VERIFIED", evidence_class=EVIDENCE_CLASS,
                                terminal_status="SUCCESS", response_sha256=sha256(result))
            except GeminiApiError as exc:
                error = exc
            finally:
                meta.update(completed_at=utc_now(), duration_seconds=time.monotonic() - start)
                if error:
                    meta.update(terminal_status="ERROR", error_category=type(error).__name__)
                write_json(evidence_path, meta)
                if self.on_attempt:
                    self.on_attempt(meta)
            if error is None:
                return result, meta
            if not isinstance(error, ApiTransientError) or retry == self.max_retries or delay > 60:
                raise error
            time.sleep(delay)
