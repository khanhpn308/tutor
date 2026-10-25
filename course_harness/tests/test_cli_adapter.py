"""Tests for CLI Adapter safety, model pinning, AGY JSON envelope validation, and manual handoff."""

import json
import os
import shutil
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from course_harness.cli_adapter import (
    AgyAdapter,
    CliExecutionError,
    ModelUnavailableError,
    redact_signed_urls,
)


class TestCliAdapter(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_signed_url_redaction(self):
        raw_text = (
            "Link Video MP4: [Xem Video]"
            "(https://d3c33hcgiwev3.cloudfront.net/VvFDB.mp4?Expires=1792886400"
            "&Signature=secret123456&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)\n"
            "Audio: (https://s3.amazonaws.com/test.mp3?X-Amz-Security-Token=xyz987&X-Amz-Signature=sig456)"
        )
        safe = redact_signed_urls(raw_text)
        self.assertNotIn("secret123456", safe)
        self.assertNotIn("xyz987", safe)
        self.assertIn("Expires=[REDACTED]", safe)
        self.assertIn("Signature=[REDACTED]", safe)
        self.assertIn("Key-Pair-Id=[REDACTED]", safe)
        self.assertIn("X-Amz-Security-Token=[REDACTED]", safe)

    def test_model_pinning_enforcement(self):
        """Adapter must reject any model name other than gemini-3.8-flash-high without falling back."""
        adapter = AgyAdapter(
            mode="mock",
            model="gemini-1.5-pro",  # Unauthorized model
            evidence_dir=self.test_dir,
        )
        with self.assertRaises(ModelUnavailableError) as ctx:
            adapter.verify_environment()
        self.assertIn("Model pinning violation", str(ctx.exception))

        with self.assertRaises(ModelUnavailableError) as ctx:
            adapter.invoke("prompt", "worker", "M01-L01")
        self.assertIn("not permitted", str(ctx.exception))

    def test_manual_handoff_mode(self):
        """Manual mode prepares prompt and instruction file, and reads valid output."""
        adapter = AgyAdapter(
            mode="manual_cli_handoff",
            evidence_dir=self.test_dir,
        )
        prompt = "Draft lesson content here..."
        # First call when output file does not yet exist
        with self.assertRaises(CliExecutionError) as ctx:
            adapter.invoke(prompt, "worker", "M01-L01", step_attempt=1)
        self.assertIn("MANUAL_HANDOFF_REQUIRED", str(ctx.exception))

        # Check instruction file and metadata were created
        instruction_path = os.path.join(self.test_dir, "handoff_worker_M01-L01_att1.md")
        meta_path = os.path.join(self.test_dir, "handoff_worker_M01-L01_att1.json")
        self.assertTrue(os.path.exists(instruction_path))
        self.assertTrue(os.path.exists(meta_path))

        with open(meta_path, "r") as mf:
            m_data = json.load(mf)
        self.assertIn("request_id", m_data)
        self.assertEqual(m_data["lesson_id"], "M01-L01")
        self.assertEqual(m_data["consumed"], False)

        # Simulate user supplying the output file
        output_path = os.path.join(self.test_dir, "output_worker_M01-L01_att1.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# User Supplied Lesson Content")

        # Second call: should now read the output and succeed
        content, meta = adapter.invoke(prompt, "worker", "M01-L01", step_attempt=1)
        self.assertEqual(content, "# User Supplied Lesson Content")
        self.assertEqual(meta["mode"], "manual_cli_handoff")
        self.assertEqual(meta["model_verified"], "NOT_VERIFIED")
        self.assertIsNotNone(meta["request_id"])

        # Check handoff metadata marked consumed
        with open(meta_path, "r") as mf:
            m_data2 = json.load(mf)
        self.assertTrue(m_data2["consumed"])

    def test_manual_handoff_rejects_reused_output(self):
        """Manual mode must reject subsequent invocations using an already-consumed handoff request."""
        adapter = AgyAdapter(
            mode="manual_cli_handoff",
            evidence_dir=self.test_dir,
        )
        prompt = "Draft lesson content..."
        output_path = os.path.join(self.test_dir, "output_worker_M01-L01_att1.txt")

        # First request setup
        with self.assertRaises(CliExecutionError):
            adapter.invoke(prompt, "worker", "M01-L01", step_attempt=1)

        # Write output and consume
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Content Attempt 1")
        adapter.invoke(prompt, "worker", "M01-L01", step_attempt=1)

        # Now attempting to call again with same handoff request must be rejected as REUSED
        with self.assertRaises(CliExecutionError) as ctx:
            adapter.invoke(prompt, "worker", "M01-L01", step_attempt=1)
        self.assertIn("REUSED_MANUAL_OUTPUT", str(ctx.exception))

    def test_manual_handoff_rejects_stale_output(self):
        """Manual mode must reject output file that predates the handoff instruction request."""
        adapter = AgyAdapter(
            mode="manual_cli_handoff",
            evidence_dir=self.test_dir,
        )
        output_path = os.path.join(self.test_dir, "output_worker_M01-L01_att1.txt")
        # Write an old output file with a past timestamp
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Stale previous output")
        old_time = time.time() - 3600
        os.utime(output_path, (old_time, old_time))

        # Invoke handoff: should reject the stale file
        with self.assertRaises(CliExecutionError) as ctx:
            adapter.invoke("prompt", "worker", "M01-L01", step_attempt=1)
        self.assertIn("STALE_MANUAL_OUTPUT", str(ctx.exception))

    @patch("subprocess.run")
    def test_malformed_json_envelope_rejected(self, mock_run):
        """When JSON output format is requested, malformed/non-JSON stdout must raise CliExecutionError."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Raw non-json text output from CLI crash",
            stderr="",
        )
        with self.assertRaises(CliExecutionError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertIn("MALFORMED_AGY_JSON", str(ctx.exception))

    @patch("subprocess.run")
    def test_non_dict_json_envelope_rejected(self, mock_run):
        """JSON output that is a list or scalar instead of a dict must be rejected."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(["item1", "item2"]),
            stderr="",
        )
        with self.assertRaises(CliExecutionError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertIn("MALFORMED_AGY_JSON", str(ctx.exception))

    @patch("subprocess.run")
    def test_missing_status_envelope_rejected(self, mock_run):
        """Envelope missing status field must be rejected."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"response": "Valid response text", "model": "gemini-3.8-flash-high"}),
            stderr="",
        )
        with self.assertRaises(CliExecutionError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertIn("Missing or empty 'status'", str(ctx.exception))

    @patch("subprocess.run")
    def test_invalid_agy_envelope_status(self, mock_run):
        """Non-terminal statuses like ERROR, WAITING, INTERRUPTED, FAILED must raise CliExecutionError."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        for bad_status in ["ERROR", "WAITING", "INTERRUPTED", "FAILED", "CANCELLED", "TIMEOUT"]:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps({"status": bad_status, "response": "Incomplete"}),
                stderr="",
            )
            with self.assertRaises(CliExecutionError) as ctx:
                adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
            self.assertIn("non-terminal", str(ctx.exception).lower())

    @patch("subprocess.run")
    def test_unknown_agy_envelope_status_rejected(self, mock_run):
        """Unknown or unverified status string must raise CliExecutionError."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"status": "SOME_CUSTOM_STATUS", "response": "Hello"}),
            stderr="",
        )
        with self.assertRaises(CliExecutionError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertIn("unsupported/unknown status", str(ctx.exception).lower())

    @patch("subprocess.run")
    def test_missing_or_empty_response_rejected(self, mock_run):
        """Envelope missing response field or with empty string must raise CliExecutionError."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        # Missing response field
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"status": "SUCCESS"}),
            stderr="",
        )
        with self.assertRaises(CliExecutionError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertIn("Missing 'response' field", str(ctx.exception))

        # Empty response field
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"status": "SUCCESS", "response": "   "}),
            stderr="",
        )
        with self.assertRaises(CliExecutionError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertIn("Empty 'response' text", str(ctx.exception))

    @patch("subprocess.run")
    def test_envelope_error_field_rejected(self, mock_run):
        """When envelope contains an error payload, must raise CliExecutionError even if status is omitted."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"error": "ResourceExhausted quota exceeded", "status": "ERROR"}),
            stderr="",
        )
        with self.assertRaises(CliExecutionError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertIn("error in JSON envelope", str(ctx.exception))

    @patch("subprocess.run")
    def test_agy_envelope_model_mismatch_rejected(self, mock_run):
        """If AGY envelope returns a fallback model, ModelUnavailableError must be raised."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "status": "SUCCESS",
                "model": "gemini-1.5-pro",
                "response": "Fallback response",
            }),
            stderr="",
        )
        with self.assertRaises(ModelUnavailableError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertIn("model mismatch", str(ctx.exception).lower())

    @patch("subprocess.run")
    def test_valid_recorded_envelope_success(self, mock_run):
        """Valid recorded AGY envelope succeeds and validates model."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        envelope = {
            "status": "SUCCESS",
            "model": "gemini-3.8-flash-high",
            "conversation_id": "conv-test-1234",
            "response": "# Generated Lesson Text",
            "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        }
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(envelope),
            stderr="",
        )

        resp, meta = adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertEqual(resp, "# Generated Lesson Text")
        self.assertEqual(meta["model_requested"], "gemini-3.8-flash-high")
        self.assertEqual(meta["model_reported"], "gemini-3.8-flash-high")
        self.assertEqual(meta["model_verified"], "VERIFIED")
        self.assertEqual(meta["conversation_id"], "conv-test-1234")

    @patch("subprocess.run")
    def test_model_absent_marks_not_verified(self, mock_run):
        """If envelope omits model, model_verified must be marked NOT_VERIFIED, never assuming requested model."""
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        envelope = {
            "status": "SUCCESS",
            "response": "# Lesson text without model info",
        }
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(envelope),
            stderr="",
        )

        _, meta = adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertEqual(meta["model_requested"], "gemini-3.8-flash-high")
        self.assertIsNone(meta["model_reported"])
        self.assertEqual(meta["model_verified"], "NOT_VERIFIED")

    @patch("subprocess.run")
    def test_subprocess_called_process_error_stderr_redaction(self, mock_run):
        """When CLI exits with non-zero code, stderr containing signed tokens must be redacted."""
        import subprocess
        adapter = AgyAdapter(mode="automated_cli", evidence_dir=self.test_dir)
        adapter.resolved_binary = "/bin/mock-agy"

        leak_stderr = "Error fetching https://media.example.com/audio.mp3?Signature=supersecret123&token=tok456"
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["agy"], output="", stderr=leak_stderr
        )
        with self.assertRaises(CliExecutionError) as ctx:
            adapter._invoke_automated("prompt", "p.md", "worker", "M01-L01", "json", 1)
        self.assertNotIn("supersecret123", str(ctx.exception))
        self.assertNotIn("tok456", str(ctx.exception))
        self.assertIn("Signature=[REDACTED]", str(ctx.exception))

    def test_auditor_boundary_metadata(self):
        """Auditor metadata must explicitly declare os_filesystem_sandbox as NOT_VERIFIED."""
        adapter = AgyAdapter(mode="mock", evidence_dir=self.test_dir)
        _, meta = adapter.invoke("prompt", "auditor", "M01-L07")
        self.assertIn("auditor_boundary", meta)
        boundary = meta["auditor_boundary"]
        self.assertEqual(boundary["os_filesystem_sandbox"], "NOT_VERIFIED")
        self.assertEqual(boundary["write_boundary_status"], "PROMPT_AND_CONTROLLER_ENFORCED_ONLY")
        self.assertIn("NOT_VERIFIED", boundary["verification_evidence"])


if __name__ == "__main__":
    unittest.main()
