#!/bin/bash
#SBATCH -J furnace_full
#SBATCH -A gts-dc187-ece
#SBATCH -p cpu-small
#SBATCH -q inferno
#SBATCH -N1 --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH -t2:00:00
#SBATCH -o full_run.log
#SBATCH -e full_run.log
cd /storage/scratch1/4/nbawana3/furnace-project
export OMP_NUM_THREADS=1
PY=venv/bin/python
echo "NODE=$(hostname) PY=$($PY --version 2>&1) START=$(date +%T)"
STEPS=(phase1_predictability phase1c_hyperparam_sensitivity phase1d_lightgbm \
       phase2_feature_ablation phase3_ood_probes phase4_years_in_service \
       phase4b_yis_permutation phase5_uncertainty regenerate_figures)
declare -A RC
for s in "${STEPS[@]}"; do
  echo ""; echo "================ $s  $(date +%T) ================"
  $PY "$s.py"; RC[$s]=$?
  echo "---- $s exit=${RC[$s]}  $(date +%T) ----"
done
echo ""; echo "================ SUMMARY ================"
for s in "${STEPS[@]}"; do printf "%-32s %s\n" "$s" "exit=${RC[$s]}"; done
echo "ALLDONE=$(date +%T)"
touch full_done
