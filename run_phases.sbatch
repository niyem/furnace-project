#!/bin/bash
#SBATCH -J furnace_rerun
#SBATCH -A gts-dc187-ece
#SBATCH -p cpu-small
#SBATCH -q inferno
#SBATCH -N1 --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH -t1:00:00
#SBATCH -o rerun.log
#SBATCH -e rerun.log
cd /storage/scratch1/4/nbawana3/furnace-project
export OMP_NUM_THREADS=1
echo "NODE=$(hostname) START=$(date +%T)"
echo "=== phase1 ==="; python3 phase1_predictability.py || exit 1
echo "=== phase1c ==="; python3 phase1c_hyperparam_sensitivity.py || exit 1
echo "=== phase1d ==="; python3 phase1d_lightgbm.py || exit 1
echo "ALLDONE=$(date +%T)"
touch rerun.done
