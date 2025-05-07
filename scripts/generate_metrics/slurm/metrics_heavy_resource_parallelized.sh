#!/bin/bash
###############################################################################
# metrics_array.sh – one task per (metric, strategy)
###############################################################################
#SBATCH --job-name=metrics_%A_%a
#SBATCH --account=def-cmoreau
#SBATCH --time=06:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --array=7-13                 # 3 metrics × 7 strategies
#SBATCH --output=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/generate_metrics/slurm/logs/parallelized.%a.out
#SBATCH --error=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/generate_metrics/slurm/logs/parallelized.%a.err
###############################################################################

set -euo pipefail
source /home/seann/scratch/denoise/fmriprep-denoise-benchmark/denoise/bin/activate

# ---------- hard‑coded number of real strategies in you HALFpipe runs----------------------------
N_STRATS=7                # baseline, simple, simple+gsr, scrubbing.5,
                          # scrubbing.5+gsr, aroma, compcor
METRICS=(connectome qcfc modularity)

flat=$SLURM_ARRAY_TASK_ID
METRIC=${METRICS[$((flat / N_STRATS))]}
STRAT_INDEX=$((flat % N_STRATS))

echo "Task $flat  metric=$METRIC  strategy_index=$STRAT_INDEX"

python /home/seann/scratch/denoise/fmriprep-denoise-benchmark/fmriprep_denoise/features/build_features_test_parallelized.py \
  /home/seann/scratch/halfpipe_test/test15/derivatives/denoise_0.8subjectthreshold \
  /home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-4.27.25_parallelTest \
  --dataset ds000228 \
  --fmriprep_ver fmriprep-20.2.7 \
  --atlas Schaefer2018 \
  --dimension 426 \
  --qc minimal \
  --metric "$METRIC" \
  --strategy_index "$STRAT_INDEX"