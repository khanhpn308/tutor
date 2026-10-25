# Quality gates

The specifications in `course_harness/prompts/worker.md`, `auditor.md`, `repair.md`, `visual_design_system.md` and `schemas/audit.schema.json` remain authoritative. Native packets supply their inputs, not a different educational rubric.

Use all eight canonical Rubric 2.0 dimensions: SOURCE_FIDELITY, CONTENT_COMPLETENESS, PEDAGOGICAL_QUALITY, VISUAL_PEDAGOGY, TERMINOLOGY_CONSISTENCY, SOURCE_TRACEABILITY, CLARITY_ORGANIZATION and FORMATTING. Deterministic weighted score must be >=90, with zero HIGH/BLOCKING findings, no FAILED dimension, and only the existing justified NOT_APPLICABLE exemptions. Never upgrade FAIL or INCONCLUSIVE to PASS.

Preserve original source meaning, numerical claims and real locators. Missing quiz options, answer keys or templates remain missing. INCOMPLETE must have a natural Vietnamese explanation of its source limitations. Hypothetical examples must be labeled in Vietnamese and must not borrow fake source timestamps. Never expose machine enum labels, transport JSON or provenance bookkeeping in student prose.

Visual-First means diagrams that explain the source, with captions, alt text, adjacent discussion and correct arrows. Native production accepts conceptual Mermaid diagrams rendered locally to SVG. No external/embedded raster images or recognizable likenesses. Instructor/author photos, portraits, avatars, headshots, screenshots and thumbnails are forbidden. Do not use a person's name as a diagram portrait. Static checks cannot prove absence of all possible likenesses or assess layout suitability, so every published visual remains pending Human Visual Review.

A visual manifest binds every figure ID to its actual .mmd/.svg file and exact SHA256. Normalize links BEFORE auditing. Any later candidate/visual change invalidates the audit. Blocking structural errors, unsafe paths, unbound figures, corrupt SVG, source/checksum differences or machine metadata leaks prevent advancement.

Auditor reads the exact finalized candidate in a new AGY context with no Worker reasoning or prior verdict. It does not modify files. Repairs need a fresh audit and are limited to 2 educational rounds. Python recomputes scores, validates schema and bindings, and rejects contradictions. Automatic production PASS does not grant HUMAN_ACCEPTED or human visual acceptance. Same-family model errors can remain correlated despite context separation.
