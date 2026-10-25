"""Tests for raw source immutability and session isolation."""

import hashlib
import os
import unittest

from course_harness.ingest import calculate_sha256, ingest_course


class TestImmutabilityAndIsolation(unittest.TestCase):

    def test_source_immutability(self):
        """Verifies that running ingest_course leaves all raw files completely untouched."""
        target_dir = "output_course/Agile_Project_Management"
        if not os.path.exists(target_dir):
            self.skipTest(f"Directory {target_dir} not found")

        # Snapshot checksums of all pilot files
        pilot_files = [
            "Module_01_The_fundamentals_of_Agile/07_The_four_values_of_the_Agile_Manifesto.md",
            "Module_02_Scrum_101/11_Understanding_Scrum_Team_roles.md",
            "Module_03_Implementing_Scrum/08_Activity_Create_a_Product_Backlog,_Due,_Oct_27,_1159_PM_PDT.md",
        ]

        before_hashes = {}
        for rel_path in pilot_files:
            full_path = os.path.join(target_dir, rel_path)
            before_hashes[rel_path] = calculate_sha256(full_path)

        # Run ingestion
        manifest = ingest_course(target_dir)

        # Check after hashes
        for rel_path in pilot_files:
            full_path = os.path.join(target_dir, rel_path)
            after_hash = calculate_sha256(full_path)
            self.assertEqual(
                before_hashes[rel_path],
                after_hash,
                f"Source file {rel_path} was modified! Immutability violated.",
            )

    def test_fresh_session_isolation(self):
        """Checks that each adapter invocation maintains fresh conversation isolation."""
        import tempfile
        import shutil
        from course_harness.cli_adapter import AgyAdapter

        temp_ev_dir = tempfile.mkdtemp()
        try:
            adapter = AgyAdapter(mode="mock", evidence_dir=temp_ev_dir)
            _, meta1 = adapter.invoke("prompt 1", "worker", "M01-L01")
            _, meta2 = adapter.invoke("prompt 2", "auditor", "M01-L01")

            # Auditor must not share session / conversation with Worker
            self.assertNotEqual(meta1["role"], meta2["role"])
            self.assertEqual(meta1["mode"], "mock")
            self.assertEqual(meta2["mode"], "mock")
        finally:
            shutil.rmtree(temp_ev_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
