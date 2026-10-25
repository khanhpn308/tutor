"""Tests for Course Ingestion, Hashing, and Source Classification."""

import os
import tempfile
import unittest

from course_harness.ingest import (
    calculate_sha256,
    classify_source_content,
    extract_locators,
    ingest_course,
)


class TestIngest(unittest.TestCase):

    def test_classify_video_transcript(self):
        title = "🎥 The four values of the Agile Manifesto"
        content = (
            "## 📜 Lời giảng viên (Transcript)\n"
            "Play video starting at ::1 and follow transcript\n"
            "0:01\nHi there. Now that you're more familiar..."
        )
        source_type, status, meta = classify_source_content(title, content, "07_The_four_values.md")
        self.assertEqual(source_type, "VIDEO_TRANSCRIPT")
        self.assertEqual(status, "AVAILABLE")
        self.assertTrue(meta["has_timestamps"])

    def test_classify_reading(self):
        title = "📖 Understanding Scrum Team roles"
        content = "# Understanding Scrum Team roles\nEach Scrum Team member plays a vital role..."
        source_type, status, meta = classify_source_content(title, content, "11_roles.md")
        self.assertEqual(source_type, "READING")
        self.assertEqual(status, "AVAILABLE")

    def test_classify_locked_content(self):
        title = "📖 Activity Exemplar: Create a Product Backlog, Locked"
        content = "## Complete previous item to unlock\nIf you have completed the previous item..."
        source_type, status, meta = classify_source_content(title, content, "09_Exemplar_Locked.md")
        self.assertEqual(status, "LOCKED")

    def test_classify_incomplete_quiz(self):
        title = "📝 Activity: Create a Product Backlog"
        content = (
            "Activity Overview\n...\n"
            "### Câu 1:\n"
            "Question 1 details...\n"
            "---\n"
            "### Câu 2:\n"
            "Select the action that best completes...\n"
            "---\n"
            "### Câu 3:\n"
            "Which of the following?\n"
        )
        source_type, status, meta = classify_source_content(title, content, "08_Activity.md")
        self.assertEqual(source_type, "ACTIVITY")
        self.assertEqual(status, "INCOMPLETE")

    def test_extract_locators(self):
        content = (
            "# Main Title\n"
            "Play video starting at :1:51\n"
            "1:51\n"
            "Let's discuss individuals and interactions.\n"
            "## Section 2: Principles\n"
            "### Câu 1: Review\n"
        )
        locators = extract_locators(content)
        loc_types = [l["type"] for l in locators]
        loc_values = [l["locator"] for l in locators]

        self.assertIn("heading_h1", loc_types)
        self.assertIn("Main Title", loc_values)
        self.assertIn("timestamp", loc_types)
        self.assertIn("1:51", loc_values)
        self.assertIn("Section 2: Principles", loc_values)
        self.assertIn("### Câu 1", [v.split(":")[0] for v in loc_values])

    def test_hashing_stability(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as f:
            f.write("Deterministic Content 12345")
            f_path = f.name
        try:
            h1 = calculate_sha256(f_path)
            h2 = calculate_sha256(f_path)
            self.assertEqual(h1, h2)
            self.assertEqual(len(h1), 64)
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)


if __name__ == "__main__":
    unittest.main()
