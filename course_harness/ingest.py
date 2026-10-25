"""Deterministic Ingestion and Source Classification for Course Harness.

Traverses raw course directories, calculates SHA256 hashes, classifies source types,
extracts locators (headings, sections, timestamps), detects incomplete/locked status,
and generates the authoritative course manifest.json.
Raw markdown sources remain strictly immutable.
"""

import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

MODULE_NUM_RE = re.compile(r'Module_0?(\d+)', re.IGNORECASE)
FILE_NUM_RE = re.compile(r'^0?(\d+)_')
TIMESTAMP_RE = re.compile(r'(\b\d{1,2}:\d{2}(?::\d{2})?\b)')
HEADING_RE = re.compile(r'^(#{1,4})\s+(.+)$', re.MULTILINE)
SIGNED_URL_RE = re.compile(r'(https?://[^\s)"]+?\?[^\s)"]+)')


def calculate_sha256(filepath: str) -> str:
    """Computes SHA256 checksum of a file without modifying it."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def classify_source_content(
    title: str,
    content: str,
    filename: str
) -> Tuple[str, str, Dict[str, Any]]:
    """Determines source type and availability status based on content heuristics.
    
    Returns:
        (source_type, status, metadata_details)
    """
    lower_content = content.lower()
    lower_title = title.lower()
    lower_file = filename.lower()

    # 1. Detect LOCKED status
    if "locked" in lower_title or "locked" in lower_file or "complete previous item to unlock" in lower_content:
        status = "LOCKED"
    elif not content.strip():
        status = "UNAVAILABLE"
    else:
        status = "AVAILABLE"

    # 2. Detect Source Type
    if "glossary" in lower_title or "glossary" in lower_file:
        source_type = "GLOSSARY"
    elif "wrap-up" in lower_title or "wrap-up" in lower_file or "course wrap-up" in lower_content:
        source_type = "WRAP_UP"
    elif "reflection:" in lower_title or "reflect and connect" in lower_title:
        source_type = "REFLECTION"
    elif "activity:" in lower_title or "activity exemplar" in lower_title or "activity" in lower_file:
        source_type = "ACTIVITY"
    elif "test your knowledge" in lower_title or "challenge" in lower_title or "quiz" in lower_title:
        source_type = "QUIZ"
    elif "🎥" in title or "transcript" in lower_content or "play video starting at" in lower_content:
        source_type = "VIDEO_TRANSCRIPT"
    elif "📖" in title or "reading" in lower_content:
        source_type = "READING"
    else:
        # Default fallback by icon/content
        if "🎥" in content:
            source_type = "VIDEO_TRANSCRIPT"
        elif "📖" in content:
            source_type = "READING"
        else:
            source_type = "READING"

    # 3. Check for INCOMPLETE content in quizzes and activities
    if status == "AVAILABLE" and source_type in ("QUIZ", "ACTIVITY"):
        has_questions = bool(re.search(r'###\s+Câu\s+\d+|Question\s+\d+', content, re.IGNORECASE))
        # Look for missing answer choices or incomplete question blocks
        # e.g., '### Câu 2:' followed immediately by another '### Câu 3:' without answers
        empty_question_pattern = re.search(r'###\s+Câu\s+\d+:?\s*\n\s*([^\n]+)\n\s*---\s*\n\s*###\s+Câu', content)
        if has_questions and empty_question_pattern:
            status = "INCOMPLETE"

    metadata = {
        "has_timestamps": bool(TIMESTAMP_RE.search(content)),
        "has_signed_media": bool(SIGNED_URL_RE.search(content)),
    }

    return source_type, status, metadata


def extract_locators(content: str) -> List[Dict[str, str]]:
    """Extracts structural locators (headings, timestamps, steps) for audit grounding."""
    locators = []
    
    # Extract headings
    for match in HEADING_RE.finditer(content):
        level = len(match.group(1))
        heading_text = match.group(2).strip()
        locators.append({
            "type": f"heading_h{level}",
            "locator": heading_text,
            "char_offset": match.start(),
        })

    # Extract timestamps
    for match in TIMESTAMP_RE.finditer(content):
        ts = match.group(1)
        # Avoid duplicate consecutive timestamps
        if not locators or locators[-1].get("locator") != ts:
            locators.append({
                "type": "timestamp",
                "locator": ts,
                "char_offset": match.start(),
            })

    # Extract question markers
    for match in re.finditer(r'(###\s+Câu\s+\d+|Step\s+\d+:[^\n]+)', content, re.IGNORECASE):
        locators.append({
            "type": "section_anchor",
            "locator": match.group(1).strip(),
            "char_offset": match.start(),
        })

    # Sort by character offset
    locators.sort(key=lambda x: x["char_offset"])
    # Clean char_offset from final output for cleaner manifest
    return [{"type": item["type"], "locator": item["locator"]} for item in locators]


def ingest_course(source_dir: str, output_manifest_path: Optional[str] = None) -> Dict[str, Any]:
    """Scans and ingests the raw course directory deterministically."""
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    course_id = os.path.basename(os.path.normpath(source_dir))

    # Find modules
    module_dirs = []
    for entry in os.listdir(source_dir):
        full_entry = os.path.join(source_dir, entry)
        if os.path.isdir(full_entry):
            m = MODULE_NUM_RE.search(entry)
            module_num = int(m.group(1)) if m else 999
            module_dirs.append((module_num, entry, full_entry))
    
    # Sort modules numerically
    module_dirs.sort(key=lambda x: x[0])

    manifest = {
        "course_id": course_id,
        "source_root": source_dir,
        "total_modules": len(module_dirs),
        "total_lessons": 0,
        "modules": {},
        "lessons": {},
    }

    total_lessons = 0

    for mod_num, mod_name, mod_path in module_dirs:
        module_id = f"M{mod_num:02d}"
        module_title = mod_name.replace(f"Module_{mod_num:02d}_", "").replace("_", " ")

        files = [f for f in os.listdir(mod_path) if f.endswith(".md")]
        
        # Sort files numerically
        def file_sort_key(f_name: str) -> Tuple[int, str]:
            m = FILE_NUM_RE.match(f_name)
            if m:
                return int(m.group(1)), f_name
            return 999, f_name

        files.sort(key=file_sort_key)

        module_entry = {
            "module_id": module_id,
            "dir_name": mod_name,
            "title": module_title,
            "lesson_count": len(files),
            "lesson_ids": [],
        }

        for filename in files:
            file_path = os.path.join(mod_path, filename)
            sha256 = calculate_sha256(file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title from first heading or filename
            first_line = content.splitlines()[0] if content.splitlines() else filename
            title_match = re.search(r'^#\s*(.+)$', first_line)
            title = title_match.group(1).strip() if title_match else filename.replace(".md", "").replace("_", " ")

            m_file = FILE_NUM_RE.match(filename)
            lesson_num = int(m_file.group(1)) if m_file else 99
            lesson_id = f"{module_id}-L{lesson_num:02d}"

            source_type, status, meta = classify_source_content(title, content, filename)
            locators = extract_locators(content)

            lesson_entry = {
                "lesson_id": lesson_id,
                "module_id": module_id,
                "filename": filename,
                "relative_path": os.path.relpath(file_path, source_dir),
                "title": title,
                "source_type": source_type,
                "status": status,
                "source_sha256": sha256,
                "char_count": len(content),
                "locators_count": len(locators),
                "locators": locators[:25],  # Keep representative locators in manifest
                "has_timestamps": meta["has_timestamps"],
                "has_signed_media": meta["has_signed_media"],
            }

            manifest["lessons"][lesson_id] = lesson_entry
            module_entry["lesson_ids"].append(lesson_id)
            total_lessons += 1

        manifest["modules"][module_id] = module_entry

    manifest["total_lessons"] = total_lessons

    if output_manifest_path:
        os.makedirs(os.path.dirname(output_manifest_path), exist_ok=True)
        with open(output_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest
