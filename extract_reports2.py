"""
Quick fix: extract the two reports that the first pass missed.
- Caracteristiques Foyers (filename has e-acute)
- Rapport_Tests Cathy 2021 (substring matcher fell over)
"""
from pathlib import Path
from docx import Document

ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project/data/raw")
OUT = Path("/storage/scratch1/4/nbawana3/furnace-project/outputs/report_extracts")
OUT.mkdir(parents=True, exist_ok=True)

PATTERNS = [
    "**/Caract*Foyers*.docx",
    "**/Rapport_Tests Cathy 2021*.docx",
]

count = 0
for pat in PATTERNS:
    matches = list(ROOT.glob(pat))
    print(f"pattern {pat!r}: {len(matches)} match(es)")
    for p in matches:
        doc = Document(str(p))
        parts = [par.text for par in doc.paragraphs if par.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                rt = " | ".join(c.text.strip() for c in row.cells)
                if rt.strip(" |"):
                    parts.append("[TABLE-ROW] " + rt)
        text = "\n".join(parts)
        out = OUT / (p.stem + ".txt")
        out.write_text(text, encoding="utf-8")
        print(f"  OK: {p.name} -> {out.name} ({len(text)} chars)")
        count += 1

print(f"Total extracted: {count}")
