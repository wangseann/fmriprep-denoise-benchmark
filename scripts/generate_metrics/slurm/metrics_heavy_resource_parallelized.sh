#!/bin/bash
###############################################################################
#  metrics_array.sh  – one Slurm array task per (metric, strategy) combination
###############################################################################

##############################  SBATCH HEADERS  ###############################
#SBATCH --job-name=metrics_%A_%a
#SBATCH --account=def-cmoreau
#SBATCH --time=06:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --array=0                  # 0-20  3 metrics × 7 strategies 
#SBATCH --output=/dev/null            # suppress Slurm’s own file
#SBATCH --error=/dev/null
###############################################################################

set -euo pipefail
trap 'echo "FAILED on line $LINENO"; exit 1' ERR

# ---- pre‑exec debug trace ---------------------------------------------------
TMP_PRE="/home/seann/scratch/denoise/fmriprep-denoise-benchmark/logs/pre_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}.log"
exec >"$TMP_PRE" 2>&1
set -x

###############################  USER CONFIG  #################################
VENV=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/denoise
INPUT_DIR=/home/seann/scratch/halfpipe_test/test15/derivatives/denoise_0.8subjectthreshold
OUTPUT_ROOT=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-4.27.25_parallelTest

DATASET=ds000228
FMRIPREP_VER=fmriprep-20.2.7
ATLAS=Schaefer2018
DIM=426
QC=minimal

SCRIPT=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/fmriprep_denoise/features/build_features_test_parallelized.py
###############################################################################

# -------------------------- activate env -------------------------------------
source "${VENV}/bin/activate"

# -------------------------- MANUAL STRATEGY LIST -----------------------------
STRATS=(baseline simple "simple+gsr" scrubbing.5 "scrubbing.5+gsr" aroma compcor)  # edit here
N_STRATS=${#STRATS[@]}

METRICS=(connectome qcfc modularity)     # length 3

flat=${SLURM_ARRAY_TASK_ID:-0}
if (( flat >= 3 * N_STRATS )); then
    echo "Array index ${flat} exceeds max combo index $((3*N_STRATS-1)); exiting."
    exit 0
fi

METRIC_INDEX=$(( flat / N_STRATS ))
STRAT_INDEX=$(( flat % N_STRATS ))

METRIC=${METRICS[$METRIC_INDEX]}
STRATEGY=${STRATS[$STRAT_INDEX]}

# -------------------------- LOG REDIRECT  ------------------------------------
LOG_DIR=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/logs
mkdir -p "${LOG_DIR}"
LOG_PREFIX=${LOG_DIR}/${DATASET}_${ATLAS}_dim-${DIM}_${QC}_${METRIC}_${STRATEGY}

# dump pre‑exec trace into final file, then redirect streams
{ cat "$TMP_PRE"; rm "$TMP_PRE"; } >"${LOG_PREFIX}.out"
exec >>"${LOG_PREFIX}.out" 2>"${LOG_PREFIX}.err"
set +x     # stop command echo

echo "Task ${flat}: metric=${METRIC}, strategy=${STRATEGY}"
echo "Started on $(date) – host: $(hostname)"
###############################################################################

###############################  RUN DRIVER  ##################################
python "$SCRIPT" \
    "${INPUT_DIR}" \
    "${OUTPUT_ROOT}" \
    --dataset "${DATASET}" \
    --fmriprep_ver "${FMRIPREP_VER}" \
    --atlas "${ATLAS}" \
    --dimension "${DIM}" \
    --qc "${QC}" \
    --metric "${METRIC}" \
    --strategy_index "${STRAT_INDEX}"