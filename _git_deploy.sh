#!/bin/bash
# Stage and commit PACE-side revision artifacts to GitHub.
# Skips raw experimental data (SOS Energie Togo / Universite de Lome; collaborator-owned)
# and the archived old modeling approach.
set -e
cd /storage/scratch1/4/nbawana3/furnace-project

# 1. Append new ignore rules to .gitignore
cat >> .gitignore <<'GIEOF'

# --- Added 2026-05-25 by the LARE revision session ---
# Raw experimental data (collaborator-owned; not for public release)
data/raw/
data/processed/

# Archive of old (pre-revision) modeling approach
outputs/_archive_old_approach/

# Local-only or temporary scratch
*.b64
GIEOF

# 2. Stage deletions of old-approach output directories
git add -u outputs/efficiency_stats/ 2>/dev/null || true
git add -u outputs/figures/ 2>/dev/null || true

# 3. Stage new content
git add .gitignore
git add *.py
git add outputs/phase1/ outputs/phase1c/ outputs/phase1d/
git add outputs/phase2/ outputs/phase3/ outputs/phase4/ outputs/phase5/
git add outputs/figures_pub/
git add outputs/report_extracts/

# 4. Summary
echo "=== STAGED CHANGES (file count) ==="
git diff --staged --stat | tail -3
echo ""
echo "=== UNTRACKED REMAINING ==="
git status --short | grep "^??" | head -10
echo ""
echo "=== DONE ==="
