"""Tests for the Repair Loop budget and max attempts transition."""

import json
import os
import shutil
import tempfile
import unittest

from course_harness.run import CourseHarnessController


class TestRepairLoop(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.yaml")

        # Create minimal test config
        config_data = {
            "models": {
                "worker": {"model": "gemini-3.8-flash-high", "effort": "high"},
                "auditor": {"model": "gemini-3.8-flash-high", "effort": "high"},
                "repair": {"model": "gemini-3.8-flash-high", "effort": "high"},
            },
            "workflow": {"max_repair_rounds": 2},
            "execution": {"mode": "mock"},
            "paths": {
                "course_id": "TestCourse",
                "source_dir": "output_course/Agile_Project_Management",
                "output_dir": os.path.join(self.test_dir, "generated"),
                "prompts_dir": "course_harness/prompts",
                "schema_path": "course_harness/schemas/audit.schema.json",
            },
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            import yaml
            yaml.dump(config_data, f)

        self.controller = CourseHarnessController(self.config_path, mode_override="mock")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mock_pass_pipeline(self):
        """In mock mode, a lesson should pass through draft and audit smoothly to MOCK_PASS."""
        res = self.controller.process_lesson("M01-L07")
        self.assertEqual(res["status"], "MOCK_PASS")
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["evidence_class"], "MOCK_SIMULATED")
        self.assertEqual(res["model_verified"], "NOT_APPLICABLE")
        self.assertTrue(os.path.exists(res["final_path"]))
        # Mock PASS cannot satisfy production resume eligibility
        source_sha = res.get("source_sha256", "0cc6f167d4d5e72eeebb9caa03c81c1e9fc709de2ee021bd212922de14233e69")
        self.assertFalse(self.controller.state_mgr.is_resumable_pass("M01-L07", source_sha))

    def test_max_repair_budget_exceeded(self):
        """When auditor repeatedly returns FAIL, controller should stop at max_repair_rounds."""
        # Monkey-patch auditor to always return FAIL
        fail_report = {
            "lesson_id": "M01-L07",
            "verdict": "FAIL",
            "summary": "Simulated persistent failure",
            "dimension_scores": {
                "SOURCE_FIDELITY": "FAILED",
                "COMPLETENESS": "MET",
                "TECHNICAL_ACCURACY": "MET",
                "TERMINOLOGY": "MET",
                "PEDAGOGICAL_QUALITY": "MET",
                "STRUCTURE": "MET",
                "TRACEABILITY": "MET"
            },
            "findings": [
                {
                    "finding_id": "F-FAIL-01",
                    "severity": "HIGH",
                    "category": "SOURCE_FIDELITY",
                    "source_locator": "00:01",
                    "draft_locator": "Section 1",
                    "description": "Persistent hallucination",
                    "required_action": "Fix hallucination"
                }
            ],
            "limitations": []
        }

        def mock_failing_auditor(lesson_meta, raw_content, draft_content, attempt):
            audit_path = os.path.join(self.controller.audits_dir, f"M01-L07_audit_v{attempt}.json")
            with open(audit_path, "w", encoding="utf-8") as f:
                json.dump(fail_report, f)
            return fail_report, audit_path

        self.controller._run_auditor = mock_failing_auditor

        res = self.controller.process_lesson("M01-L07", reset=True)
        self.assertEqual(res["status"], "NEEDS_HUMAN_REVIEW")
        self.assertEqual(res["error_category"], "MAX_REPAIR_EXCEEDED")
        self.assertEqual(res["repair_attempts"], 2)

    def test_stale_manifest_detected(self):
        """When manifest source_sha256 differs from raw file on disk, ManifestStaleError must be raised."""
        from course_harness.run import ManifestStaleError

        manifest = self.controller.get_manifest()
        # Tamper manifest in memory to simulate a stale manifest
        manifest["lessons"]["M01-L07"]["source_sha256"] = "tampered_stale_hash_12345"
        self.controller.manifest = manifest

        with self.assertRaises(ManifestStaleError) as ctx:
            self.controller.process_lesson("M01-L07")
        self.assertIn("MANIFEST_STALE", str(ctx.exception))

    def test_automated_bulk_execution_blocked(self):
        """Automated bulk module execution must be blocked under provider-use policy."""
        import sys
        from unittest.mock import patch
        from course_harness.run import main

        # Simulate CLI arguments: --module M01 in automated_cli mode
        test_args = ["run.py", "--module", "M01", "--config", self.config_path]
        # In self.config_path, change execution mode to automated_cli
        with open(self.config_path, "r") as f:
            import yaml
            cfg = yaml.safe_load(f)
        cfg["execution"]["mode"] = "automated_cli"
        with open(self.config_path, "w") as f:
            yaml.dump(cfg, f)

        with patch.object(sys, "argv", test_args), \
             patch("course_harness.cli_adapter.AgyAdapter.verify_environment", return_value={"status": "VERIFIED"}):
            exit_code = main()
            # main() catches BlockedExecutionError and returns code 3
            self.assertEqual(exit_code, 3)


if __name__ == "__main__":
    unittest.main()
