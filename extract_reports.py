"""
extract_reports.py — Extract text from LARE laboratory reports for Methods drafting.

Walks data/raw/ for the four target reports and writes plain-text extracts to
outputs/report_extracts/. Handles both .docx (paragraphs + tables) and .pdf.

Outputs:
    outputs/report_extracts/<original_basename>.txt
    outputs/report_extracts/extraction.log
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from docx import Document
import pdfplumber

ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project/data/raw")
OUT = Path("/storage/scratch1/4/nbawana3/furnace-project/outputs/report_extracts")
OUT.mkdir(parents=True, exist_ok=True)
LOG_PATH = OUT / "extraction.log"

# Substrings (case-insensitive) that should match the target report filenames.
TARGETS = [
    "caracteristiques foyers",
    "rapport_tests cathy 2021",
    "accessible energy 2019f",
    "sequoia february 2023",
]


def normalize(s: str) -> str:
    """Lowercase and collapse separators so spaces/underscores/hyphens match."""
    out = s.lower()
    for ch in ("_", "-", "."):
        out = out.replace(ch, " ")
    return " ".join(out.split())


def extract_docx(path: Path) -> str:
    doc = Document(str(path))
    parts = []
    for p in doc.paragraphs:
        if p.text.strip():
            parts.append(p.text)
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(c.text.strip() for c in row.cells)
            if row_text.strip(" |"):
                parts.append("[TABLE-ROW] " + row_text)
    return "\n".join(parts)


def extract_pdf(path: Path) -> str:
    parts = []
    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            txt = page.extract_text() or ""
            if txt.strip():
                parts.append(f"[PAGE {i}]\n{txt}")
    return "\n\n".join(parts)


def main() -> None:
    log_lines = []
    matches_seen = 0
    files_written = 0

    for dirpath, _, filenames in os.walk(ROOT):
        for fn in filenames:
            ext = fn.lower().rsplit(".", 1)[-1] if "." in fn else ""
            if ext not in ("docx", "pdf"):
                continue
            norm = normalize(fn)
            target_hit = next((t for t in TARGETS if t in norm), None)
            if target_hit is None:
                continue
            matches_seen += 1
            full = Path(dirpath) / fn
            stem = fn.rsplit(".", 1)[0]
            out_path = OUT / (stem + ".txt")
            try:
                if ext == "docx":
                    text = extract_docx(full)
                else:
                    text = extract_pdf(full)
                out_path.write_text(text, encoding="utf-8")
                files_written += 1
                msg = f"OK [{ext}] match='{target_hit}' -> {out_path.name} ({len(text)} chars)"
                log_lines.append(msg)
                print(msg)
            except Exception as e:
                msg = f"FAIL [{ext}] {fn}: {e!r}"
                log_lines.append(msg)
                print(msg, file=sys.stderr)

    summary = f"\nMatches: {matches_seen}, Successfully extracted: {files_written}"
    log_lines.append(summary)
    print(summary)
    LOG_PATH.write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
