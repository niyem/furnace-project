"""
preprocess_wbt.py — Cookstove WBT preprocessing pipeline.

Reads the raw Water Boiling Test xlsx archive at
    data/raw/Tests_Foyers_unzipped/Tests_Foyers/
and produces three outputs in data/processed/:

    wbt_long.csv     tidy long format, one row per (xlsx × phase × metric × replicate)
    wbt_wide.csv     wide ML-ready format, one row per (xlsx × replicate)
    wbt_report.txt   run summary + per-campaign coverage + validation flags

This pipeline does NOT use the legacy Final_Modified.xlsx aggregate; it reads the
original xlsx files end-to-end and reconstructs brand / format / sale-year /
material / campaign / country-of-manufacture metadata that was dropped in the
legacy flow.

Strategy spec: see PREPROCESSING.md alongside this module.
Run:
    python3 preprocess_wbt.py
"""

from __future__ import annotations

import logging
import math
import os
import re
import sys
import warnings
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

import openpyxl
import pandas as pd

warnings.filterwarnings('ignore')

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path('/storage/scratch1/4/nbawana3/furnace-project')
RAW_ROOT = PROJECT_ROOT / 'data' / 'raw' / 'Tests_Foyers_unzipped' / 'Tests_Foyers'
OUT_DIR = PROJECT_ROOT / 'data' / 'processed'

LONG_OUT = OUT_DIR / 'wbt_long.csv'
WIDE_OUT = OUT_DIR / 'wbt_wide.csv'
REPORT_OUT = OUT_DIR / 'wbt_report.txt'

# Toyola "habitat × commercial" size geometry from Dimensions_Foyers Toyola 2021.docx.
# Only these five formats have measured dimensions; other product lines (CPA, MAN,
# SEQUOIA Foyer-N, SURAJ) get NaN geometry — fill in if measurements are obtained.
STOVE_DIMS = {
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
}

# Phase headers appear in column B of the Results sheet in order.
PHASE_ORDER = ['cold', 'hot', 'simmer']

# Metric name -> short code emitted in long format.
METRIC_RULES = [
    # (substring to match in metric label, output code)
    # NOTE: keep "thermal efficiency" before "efficiency" since some sheets have just "Efficiency"
    ('thermal efficiency', 'eff'),
    ('firepower', 'fp'),
    ('burning rate', 'br'),
    ('specific fuel cons', 'sfc'),
    ('time to boil', 'tboil'),
]

# Skip temp-corrected variants — they duplicate the non-corrected metrics.
SKIP_IF_CONTAINS = ['temp-corrected', 'temp corrected']

# Replicate columns: Test 1..4 + Average sit at column indices 3..7 of the Results sheet.
REPLICATE_COLS = [(3, 'T1'), (4, 'T2'), (5, 'T3'), (6, 'T4'), (7, 'avg')]


logging.basicConfig(
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO,
    stream=sys.stdout,
)
log = logging.getLogger('preprocess_wbt')


# =============================================================================
# Records
# =============================================================================

@dataclass
class Measurement:
    """One measurement row in long format. Maps directly to a row in wbt_long.csv."""
    src_path: str
    source_kind: str          # 'wbt_template' or 'summary'
    # File-internal metadata (WBT General Information sheet)
    tester: str | None = None
    test_year: object = None  # numeric or string, stove sale year per WBT template
    location: str | None = None
    manufacturer: str | None = None
    stove_model: str | None = None
    altitude: object = None
    # Path-derived metadata
    campaign: str | None = None
    brand: str | None = None
    format: str | None = None
    sale_year: int | None = None
    material: str | None = None
    country_make: str | None = None
    # Measurement
    phase: str | None = None
    metric: str | None = None
    replicate: str | None = None  # 'T1'..'T4' / 'avg' / 'summary'
    value: float | None = None
    units: str | None = None
    # Geometry (joined from STOVE_DIMS after enrichment)
    height_cm: float | None = None
    outside_d_cm: float | None = None
    chamber_d_cm: float | None = None
    chamber_depth_cm: float | None = None
    inlet_w_cm: float | None = None
    inlet_h_cm: float | None = None
    inlet_area_cm2: float | None = None
    chamber_volume_cm3: float | None = None


# =============================================================================
# Discovery
# =============================================================================

def discover(root: Path) -> list[Path]:
    """Walk the raw root, return sorted list of xlsx files (excluding Excel lock files)."""
    files: list[Path] = []
    for p in root.rglob('*.xlsx'):
        if p.name.startswith('~'):
            continue  # Excel/Word lock files
        files.append(p)
    files.sort()
    log.info('Discovered %d xlsx files under %s', len(files), root)
    return files


# =============================================================================
# Classification
# =============================================================================

def classify(path: Path) -> tuple[str, openpyxl.Workbook | None]:
    """
    Open the workbook and decide its layout.

    Returns ('wbt_template' | 'summary' | 'unknown', workbook | None).
    Caller is responsible for closing the workbook.
    """
    try:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    except Exception as exc:
        log.warning('Open failed for %s: %s', path.name, exc)
        return 'unknown', None
    sheets = set(wb.sheetnames)
    if {'General Information', 'Results'}.issubset(sheets):
        return 'wbt_template', wb
    if sheets == {'Feuil1'} or (len(sheets) == 1 and 'Feuil1' in sheets):
        return 'summary', wb
    return 'unknown', wb


# =============================================================================
# WBT 4.2.x template parser
# =============================================================================

def _normalize_metric(label: str) -> str | None:
    """Map a raw 'metric_name' string to one of our short codes (eff / fp / br / sfc / tboil)."""
    s = label.lower()
    if any(skip in s for skip in SKIP_IF_CONTAINS):
        return None
    for needle, code in METRIC_RULES:
        if needle in s:
            return code
    return None


def _read_general_info(wb: openpyxl.Workbook) -> dict:
    """Extract per-test metadata from the General Information sheet (rows 1..25, col B values)."""
    md: dict = {}
    try:
        ws = wb['General Information']
    except KeyError:
        return md
    for row in ws.iter_rows(min_row=1, max_row=25, max_col=4, values_only=True):
        if not row or row[0] is None:
            continue
        label = str(row[0]).lower()
        value = row[1] if len(row) > 1 else None
        if 'name of tester' in label:
            md['tester'] = value
        elif 'test year' in label:
            md['test_year'] = value
        elif 'test location' in label:
            md['location'] = value
        elif 'manufactured by' in label:
            md['manufacturer'] = value
        elif 'stove type' in label or 'stove model' in label:
            md['stove_model'] = value
        elif 'altitude' in label or 'elevation' in label:
            md['altitude'] = value
    return md


def _read_results(wb: openpyxl.Workbook) -> list[dict]:
    """Walk the Results sheet; replicates detected dynamically; Average fallback computed."""
    out = []
    try:
        rows = list(wb['Results'].iter_rows(min_row=1, max_row=60, max_col=20, values_only=True))
    except KeyError:
        return out
    phase_idx = -1
    phase = None
    rep_cols = []
    avg_col = None
    for r in rows:
        if not r or len(r) < 2:
            continue
        c1 = str(r[1]).lower() if r[1] is not None else ''
        if 'high power' in c1 or 'low power' in c1:
            phase_idx += 1
            phase = PHASE_ORDER[phase_idx] if phase_idx < len(PHASE_ORDER) else None
            rep_cols = []
            avg_col = None
            for ci in range(3, len(r)):
                lbl = str(r[ci]).strip().lower() if r[ci] is not None else ''
                m = re.fullmatch(r'test\s*(\d+)', lbl)
                if m:
                    rep_cols.append((ci, f'T{m.group(1)}'))
                elif lbl in ('average', 'avg') or 'moy' in lbl:
                    avg_col = ci
            continue
        if phase is None or not rep_cols:
            continue
        metric_code = _normalize_metric(c1)
        if metric_code is None:
            continue
        units = r[2] if len(r) > 2 and r[2] is not None else None
        rep_values = []
        for col_idx, rep_label in rep_cols:
            if col_idx >= len(r):
                continue
            raw_v = r[col_idx]
            try:
                v = float(raw_v) if raw_v not in (None, '') else None
            except (TypeError, ValueError):
                v = None
            if v is None:
                continue
            rep_values.append(v)
            out.append(dict(
                phase=phase, metric=metric_code, replicate=rep_label,
                value=v, units=str(units) if units is not None else None,
            ))
        avg_v = None
        if avg_col is not None and avg_col < len(r):
            raw_avg = r[avg_col]
            try:
                avg_v = float(raw_avg) if raw_avg not in (None, '') else None
            except (TypeError, ValueError):
                avg_v = None
        if avg_v is None and rep_values:
            avg_v = sum(rep_values) / len(rep_values)
        if avg_v is not None:
            out.append(dict(
                phase=phase, metric=metric_code, replicate='avg',
                value=avg_v, units=str(units) if units is not None else None,
            ))
    return out


def parse_wbt(path: Path, wb: openpyxl.Workbook) -> list[Measurement]:
    """Parse a WBT 4.2.x template file. Caller passes the already-opened workbook."""
    md = _read_general_info(wb)
    measurements = _read_results(wb)
    src_rel = str(path.relative_to(RAW_ROOT))
    return [
        Measurement(
            src_path=src_rel, source_kind='wbt_template',
            tester=md.get('tester'),
            test_year=md.get('test_year'),
            location=md.get('location'),
            manufacturer=md.get('manufacturer'),
            stove_model=md.get('stove_model'),
            altitude=md.get('altitude'),
            phase=m['phase'], metric=m['metric'], replicate=m['replicate'],
            value=m['value'], units=m['units'],
        )
        for m in measurements
    ]


# =============================================================================
# Single-sheet summary parser (Prakash / SURAJ)
# =============================================================================

# Maps French / English column headers in summary files to our (metric, phase) codes.
_SUMMARY_HEADER_MAP = [
    # (regex on header, metric_code, phase or None if header determines phase separately)
    (re.compile(r'thermal\s*eff', re.I), 'eff', None),
    (re.compile(r'efficacit', re.I), 'eff', None),
    (re.compile(r'firepower', re.I), 'fp', None),
    (re.compile(r'puissance', re.I), 'fp', None),
    (re.compile(r'burn(ing)?\s*rate', re.I), 'br', None),
    (re.compile(r'vitesse\s*de\s*combustion', re.I), 'br', None),
    (re.compile(r'specific\s*fuel', re.I), 'sfc', None),
    (re.compile(r'consommation\s*sp', re.I), 'sfc', None),
    (re.compile(r'time\s*to\s*boil', re.I), 'tboil', None),
    (re.compile(r'temps\s*d?\'?\s*[éeb]bullition', re.I), 'tboil', None),
]

_PHASE_TOKENS = [
    (re.compile(r'cold|froid', re.I), 'cold'),
    (re.compile(r'hot|chaud', re.I), 'hot'),
    (re.compile(r'simmer|basse\s*puissance|low\s*power', re.I), 'simmer'),
]


def _infer_phase(header: str) -> str | None:
    for rx, ph in _PHASE_TOKENS:
        if rx.search(header):
            return ph
    return None


def parse_summary(path: Path, wb: openpyxl.Workbook) -> list[Measurement]:
    """
    Parse a Prakash / SURAJ single-sheet summary file.

    These files have a `Feuil1` sheet (~47×9) with a header row followed by per-stove
    summary rows. We probe the first ~5 rows for the header, then map each numeric
    column to a (metric, phase) tuple if we can recognize the column header.
    """
    src_rel = str(path.relative_to(RAW_ROOT))
    try:
        ws = wb['Feuil1']
    except KeyError:
        return []

    rows = list(ws.iter_rows(min_row=1, max_row=ws.max_row or 50, max_col=ws.max_column or 12, values_only=True))
    if not rows:
        return []

    # Find header row: first row where >= 3 non-numeric, non-empty cells
    header_row_idx = None
    for i, r in enumerate(rows[:8]):
        non_num = sum(1 for v in r if isinstance(v, str) and len(v.strip()) > 1)
        if non_num >= 3:
            header_row_idx = i
            break
    if header_row_idx is None:
        return []
    headers = [str(v).strip() if v is not None else '' for v in rows[header_row_idx]]

    # Build (col_idx -> (metric_code, phase)) mapping based on header text
    col_map: dict[int, tuple[str, str | None]] = {}
    for ci, h in enumerate(headers):
        if not h:
            continue
        metric_code = None
        for rx, code, _ in _SUMMARY_HEADER_MAP:
            if rx.search(h):
                metric_code = code
                break
        if metric_code is None:
            continue
        phase = _infer_phase(h)
        col_map[ci] = (metric_code, phase)

    if not col_map:
        return []

    # Emit one Measurement per (row × matched column) with replicate='summary'
    out: list[Measurement] = []
    for ri in range(header_row_idx + 1, len(rows)):
        r = rows[ri]
        for ci, (metric_code, phase) in col_map.items():
            if ci >= len(r):
                continue
            raw_v = r[ci]
            try:
                v = float(raw_v) if raw_v not in (None, '') else None
            except (TypeError, ValueError):
                v = None
            if v is None:
                continue
            out.append(Measurement(
                src_path=src_rel, source_kind='summary',
                phase=phase, metric=metric_code, replicate='summary',
                value=v, units=None,
            ))
    return out


# =============================================================================
# Path-derived metadata enrichment
# =============================================================================

# Format extractors — order matters; first match wins.
_RE_HXC = re.compile(r'\b(HS|HM|HL|CS|CL)\b', re.IGNORECASE)
_RE_CPA = re.compile(r'CPA\s*([1-4])', re.IGNORECASE)
_RE_MAN = re.compile(r'\bMAN\s*([0-9]+)\b', re.IGNORECASE)
_RE_FOYER_N = re.compile(r'[Ff]oyer\s*N[°o]?\s*([0-9]+)')
_RE_WM = re.compile(r'\bWM\b')
_RE_SALE_YEAR = re.compile(r'(HS|HM|HL|CS|CL)\s*(20\d{2})', re.IGNORECASE)

_SEQUOIA_MODELS = ['TCHATCHA', 'OPTIMA-BENIN', 'GLOIRE A DIEU', 'OPTIMA', 'SUPER', 'TCHA', 'TOGO']

def _extract_sequoia_model(rel_path):
    up = rel_path.upper()
    for name in _SEQUOIA_MODELS:
        if name.upper() in up:
            return name.replace(' ', '_')
    return None


def enrich_path_metadata(measurement: Measurement) -> None:
    """In place: fill campaign / brand / format / sale_year / material / country_make from src_path."""
    rel = measurement.src_path
    parts = rel.split('/')
    top = parts[0] if parts else ''
    tl = top.lower()
    rl = rel.lower()

    # Campaign = top-level directory verbatim
    measurement.campaign = top

    # Brand
    if 'toyola' in tl or 'cathy' in tl or 'fiches' in tl:
        brand = 'Toyola'
    elif 'sequoia' in tl:
        brand = 'SEQUOIA-tested'
    elif 'ghana' in tl:
        brand = 'Ghana-MAN'
    elif 'suraj' in tl:
        brand = 'Toyola-Nigeria'
    elif 'prakash' in tl:
        brand = 'Prakash'
    else:
        brand = 'Unknown'
    measurement.brand = brand

    # Country of manufacture (default Togo; specific overrides below)
    country = 'Togo'
    if 'ghana' in tl:
        country = 'Ghana'
    elif 'suraj' in tl or 'nigeria' in rl:
        country = 'Nigeria'
    if 'optima' in rl:
        country = 'Benin'  # OPTIMA = Beninese manufacturer
    measurement.country_make = country

    # Material — default clay; ceramic if SEQUOIA-tested OR specific Togo/Benin ceramic makers
    material = 'clay'
    if brand == 'SEQUOIA-tested':
        material = 'ceramic'
    if 'optima' in rl or 'tchatcha' in rl or 'farm commod' in rl:
        material = 'ceramic'
    measurement.material = material

    # Format — try brand-specific extractors
    fmt: str | None = None
    if 'CPA' in rel.upper():
        m = _RE_CPA.search(rel)
        if m:
            fmt = f'CPA{m.group(1)}'
    if fmt is None and brand == 'Ghana-MAN':
        m = _RE_MAN.search(rel)
        if m:
            fmt = f'MAN{m.group(1)}'
        elif _RE_WM.search(rel):
            fmt = 'WM'
    if fmt is None and brand == 'SEQUOIA-tested':
        fmt = _extract_sequoia_model(rel)
        if fmt is None:
            m = _RE_FOYER_N.search(rel)
            if m:
                fmt = f'F{m.group(1)}'
    if fmt is None:
        # Toyola HxC / Prakash / SURAJ
        for chunk in parts:
            m = _RE_HXC.search(chunk)
            if m:
                fmt = m.group(1).upper()
                break
    measurement.format = fmt

    # Sale year (Toyola filenames pattern HS2014.xlsx etc.)
    fname = parts[-1] if parts else ''
    sy = _RE_SALE_YEAR.search(fname)
    if sy:
        try:
            measurement.sale_year = int(sy.group(2))
        except ValueError:
            pass


def attach_geometry(measurement: Measurement) -> None:
    """In place: copy STOVE_DIMS values into measurement if the format is HS/HM/HL/CS/CL."""
    dims = STOVE_DIMS.get(measurement.format or '')
    if not dims:
        return
    for k, v in dims.items():
        setattr(measurement, k, v)
    # Derived geometry
    measurement.inlet_area_cm2 = dims['inlet_w_cm'] * dims['inlet_h_cm']
    measurement.chamber_volume_cm3 = (
        math.pi * (dims['chamber_d_cm'] / 2) ** 2 * dims['chamber_depth_cm']
    )


# =============================================================================
# Validation
# =============================================================================

VALID_RANGES = {
    'eff': (0.0, 1.0),       # thermal efficiency as fraction
    'fp': (0.0, 1e5),        # firepower in watts (0–100 kW)
    'br': (0.0, 1e3),        # burning rate g/min
    'sfc': (0.0, 1e4),       # specific fuel consumption g/liter
    'tboil': (0.0, 1e3),     # minutes
}


def validate(df: pd.DataFrame) -> list[str]:
    """Return a list of warning strings (does not modify df)."""
    warns: list[str] = []
    for metric, (lo, hi) in VALID_RANGES.items():
        sub = df[df['metric'] == metric]
        if sub.empty:
            continue
        oor = sub[(sub['value'] < lo) | (sub['value'] > hi)]
        if len(oor) > 0:
            warns.append(f'metric={metric}: {len(oor)} values out of range [{lo}, {hi}]')
    # Duplicate detection
    key_cols = ['src_path', 'replicate', 'phase', 'metric']
    if df[key_cols].duplicated().any():
        n = int(df[key_cols].duplicated().sum())
        warns.append(f'{n} duplicate (src_path, replicate, phase, metric) rows')
    # NaN format coverage
    nan_fmt = df[df['format'].isna()]
    if len(nan_fmt) > 0:
        camps = nan_fmt['campaign'].value_counts().head(8).to_dict()
        warns.append(f'{len(nan_fmt)} rows with NaN format; top campaigns: {camps}')
    return warns


# =============================================================================
# Long → wide pivot
# =============================================================================

ID_COLS = [
    'src_path', 'replicate', 'replicate_kind',
    'source_kind', 'campaign', 'brand', 'format', 'sale_year', 'material', 'country_make',
    'tester', 'test_year', 'location', 'manufacturer', 'stove_model', 'altitude',
    'height_cm', 'outside_d_cm', 'chamber_d_cm', 'chamber_depth_cm',
    'inlet_w_cm', 'inlet_h_cm', 'inlet_area_cm2', 'chamber_volume_cm3',
]


def to_wide(long_df: pd.DataFrame) -> pd.DataFrame:
    """Pivot long format -> wide. Columns: id cols + metric_phase columns."""
    if long_df.empty:
        return pd.DataFrame()
    df = long_df.copy()
    df['replicate_kind'] = df['replicate'].apply(
        lambda r: 'average' if r == 'avg' else ('summary' if r == 'summary' else 'replicate')
    )
    df['_col'] = df['metric'] + '_' + df['phase']
    pivot = (
        df.groupby(ID_COLS + ['_col'], dropna=False, observed=True)['value']
          .mean()
          .unstack('_col')
          .reset_index()
    )
    pivot.columns.name = None
    return pivot


# =============================================================================
# Orchestration
# =============================================================================

def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = discover(RAW_ROOT)

    all_measurements: list[Measurement] = []
    n_wbt = 0
    n_summary = 0
    n_unknown = 0
    n_empty = 0

    for i, path in enumerate(files, 1):
        if i % 25 == 0 or i == len(files):
            log.info('progress %d/%d  wbt=%d  summary=%d  unknown=%d  empty=%d',
                     i, len(files), n_wbt, n_summary, n_unknown, n_empty)
        kind, wb = classify(path)
        if wb is None:
            n_unknown += 1
            continue
        try:
            if kind == 'wbt_template':
                ms = parse_wbt(path, wb)
                n_wbt += 1 if ms else 0
                n_empty += 1 if not ms else 0
            elif kind == 'summary':
                ms = parse_summary(path, wb)
                n_summary += 1 if ms else 0
                n_empty += 1 if not ms else 0
            else:
                n_unknown += 1
                continue
        finally:
            wb.close()

        for m in ms:
            enrich_path_metadata(m)
            attach_geometry(m)
        all_measurements.extend(ms)

    log.info('Total measurements: %d', len(all_measurements))
    if not all_measurements:
        log.error('No measurements extracted; aborting.')
        sys.exit(1)

    long_df = pd.DataFrame([asdict(m) for m in all_measurements])
    warns = validate(long_df)

    log.info('Writing long format: %s  (%d rows × %d cols)',
             LONG_OUT, len(long_df), long_df.shape[1])
    long_df.to_csv(LONG_OUT, index=False)

    wide_df = to_wide(long_df)

    # ---- Sentinel-zero correction for eff_simmer -----------------------------
    # The Tests_SURAJ_2023 and Fichiers_Tests_Prakash_OK_OK source templates use
    # a literal 0.0 in the simmer-phase efficiency cell to indicate "not measured"
    # while leaving the corresponding firepower and burn-rate cells blank (NaN).
    # Without correction these 90 sentinel zeros propagate as real measurements
    # and bias eff_simmer modeling toward apparent underperformance while
    # artificially inflating the eff_simmer intraclass correlation. Treat them
    # as missing here so eff_simmer is consistent with the other simmer columns.
    SENTINEL_CAMPAIGNS = ('Tests_SURAJ_2023', 'Fichiers_Tests_Prakash_OK_OK')
    if 'eff_simmer' in wide_df.columns and 'campaign' in wide_df.columns:
        before = (wide_df['eff_simmer'] == 0).sum()
        sentinel_mask = (wide_df['eff_simmer'] == 0) & wide_df['campaign'].isin(SENTINEL_CAMPAIGNS)
        n_corrected = int(sentinel_mask.sum())
        wide_df.loc[sentinel_mask, 'eff_simmer'] = float('nan')
        log.info('Sentinel-zero correction: replaced %d eff_simmer zeros with NaN '
                 '(campaigns: %s; remaining zeros: %d)',
                 n_corrected, SENTINEL_CAMPAIGNS, int(before) - n_corrected)
    # --------------------------------------------------------------------------

    log.info('Writing wide format: %s  (%d rows × %d cols)',
             WIDE_OUT, len(wide_df), wide_df.shape[1])
    wide_df.to_csv(WIDE_OUT, index=False)

    write_report(long_df, wide_df, warns, n_wbt, n_summary, n_unknown, n_empty, len(files))
    log.info('Done. Report: %s', REPORT_OUT)


def write_report(long_df: pd.DataFrame, wide_df: pd.DataFrame, warns: list[str],
                 n_wbt: int, n_summary: int, n_unknown: int, n_empty: int,
                 n_files: int) -> None:
    lines = []
    lines.append('Cookstove WBT preprocessing run report')
    lines.append('=' * 70)
    lines.append(f'Raw root: {RAW_ROOT}')
    lines.append(f'Files discovered: {n_files}')
    lines.append(f'  parsed as WBT 4.2.x template: {n_wbt}')
    lines.append(f'  parsed as single-sheet summary: {n_summary}')
    lines.append(f'  unknown / open-failed: {n_unknown}')
    lines.append(f'  empty (no measurements extracted): {n_empty}')
    lines.append('')
    lines.append(f'Long format rows: {len(long_df)}')
    lines.append(f'Wide format rows: {len(wide_df)}')
    lines.append('')
    lines.append('Per-brand row counts (long format):')
    lines.append(long_df['brand'].value_counts(dropna=False).to_string())
    lines.append('')
    lines.append('Per-material row counts (long format):')
    lines.append(long_df['material'].value_counts(dropna=False).to_string())
    lines.append('')
    lines.append('Per-format row counts (long format):')
    lines.append(long_df['format'].value_counts(dropna=False).to_string())
    lines.append('')
    lines.append('Per (campaign, format) wide-row counts:')
    if not wide_df.empty:
        lines.append(wide_df.groupby(['campaign', 'format'], dropna=False)
                     .size().to_string())
    lines.append('')
    lines.append('Phase × metric (long format counts):')
    lines.append(long_df.groupby(['phase', 'metric']).size().to_string())
    lines.append('')
    lines.append('Efficiency (eff) descriptive stats by phase:')
    eff = long_df[long_df['metric'] == 'eff']
    if not eff.empty:
        lines.append(eff.groupby('phase')['value'].describe()
                     [['count', 'mean', 'std', 'min', 'max']].to_string())
    lines.append('')
    lines.append('Validation warnings:')
    if not warns:
        lines.append('  (none)')
    else:
        for w in warns:
            lines.append(f'  - {w}')

    REPORT_OUT.write_text('\n'.join(lines))


if __name__ == '__main__':
    run()
