"""
fix_stove_dims.py - Replace STOVE_DIMS in preprocess_wbt.py with values
from the SOS Energie Togo 2019 Accessible Energy report (authoritative source).
"""
from __future__ import annotations
import re
from pathlib import Path

SRC = Path("/storage/scratch1/4/nbawana3/furnace-project/preprocess_wbt.py")
text = SRC.read_text(encoding="utf-8")

NEW = '''STOVE_DIMS = {
    "HS": dict(height_cm=21.0, outside_d_cm=26.5, chamber_d_cm=19.5,
               chamber_depth_cm=5.5, inlet_w_cm=5.5, inlet_h_cm=9.5),
    "HM": dict(height_cm=24.0, outside_d_cm=31.0, chamber_d_cm=22.0,
               chamber_depth_cm=6.0, inlet_w_cm=5.5, inlet_h_cm=10.5),
    "HL": dict(height_cm=26.0, outside_d_cm=34.0, chamber_d_cm=22.5,
               chamber_depth_cm=6.5, inlet_w_cm=7.0, inlet_h_cm=12.0),
    "CS": dict(height_cm=33.0, outside_d_cm=45.0, chamber_d_cm=31.0,
               chamber_depth_cm=10.0, inlet_w_cm=9.0, inlet_h_cm=16.0),
    "CL": dict(height_cm=40.0, outside_d_cm=48.0, chamber_d_cm=34.5,
               chamber_depth_cm=10.0, inlet_w_cm=12.0, inlet_h_cm=21.5),
}'''

pattern = re.compile(r"^STOVE_DIMS = \{.*?^\}", re.DOTALL | re.MULTILINE)
new_text, n = pattern.subn(NEW, text, count=1)
if n != 1:
    raise SystemExit(f"FAIL: matched {n} blocks; expected exactly 1")

SRC.write_text(new_text, encoding="utf-8")
print(f"OK: replaced STOVE_DIMS block ({len(text)} -> {len(new_text)} chars)")
