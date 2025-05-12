#!/bin/bash
###############################################################################
# metrics_array.sh – one task per (metric, strategy)
###############################################################################
#SBATCH --job-name=dev_metrics_%A_%a
#SBATCH --account=def-cmoreau
#SBATCH --time=15:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --array=0-26                 # 3 metrics × 9 strategies 0-8,9-17,18-26
#SBATCH --output=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/generate_metrics/slurm/logs/parallelized_dev.%a.out
#SBATCH --error=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/generate_metrics/slurm/logs/parallelized_dev.%a.err
###############################################################################

set -euo pipefail
source /home/seann/scratch/denoise/fmriprep-denoise-benchmark/denoise/bin/activate

# ---------- hard‑coded number of real strategies in you HALFpipe runs----------------------------
N_STRATS=9                # baseline, simple, simple+gsr, scrubbing.5,
                          # scrubbing.5+gsr, aroma, compcor
METRICS=(connectome qcfc modularity)

flat=$SLURM_ARRAY_TASK_ID
METRIC=${METRICS[$((flat / N_STRATS))]}
STRAT_INDEX=$((flat % N_STRATS))

echo "Task $flat  metric=$METRIC  strategy_index=$STRAT_INDEX"

# python /home/seann/scratch/denoise/fmriprep-denoise-benchmark/fmriprep_denoise/features/build_features_test_parallelized.py \
#   /home/seann/scratch/halfpipe_test/test15/derivatives/denoise_0.8subjectthreshold \
#   /home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-4.27.25_parallelTest \
#   --dataset ds000228 \
#   --fmriprep_ver fmriprep-20.2.7 \
#   --atlas Schaefer2018 \
#   --dimension 426 \
#   --qc minimal \
#   --metric "$METRIC" \
#   --strategy_index "$STRAT_INDEX"

python /home/seann/scratch/denoise/fmriprep-denoise-benchmark/fmriprep_denoise/features/build_features_test_parallelized.py \
  /home/seann/scratch/halfpipe_test/25-04-25_ds228_halfpipe-1.2.3_fmriprep-25.0.0_dvars-corrected/derivatives/denoise \
  /home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-5.08.25 \
  --dataset ds000228 \
  --fmriprep_ver fmriprep-25.0.0 \
  --atlas schaefer400 \
  --dimension 419 \
  --qc stringent \
  --metric "$METRIC" \
  --strategy_index "$STRAT_INDEX"



###############################################################################
# Checklist for running this script:
# 1. Ensure the SLURM_ARRAY_TASK_ID is correctly set for the job array.
# 2. Verify the paths to the Python script and required directories:
#    - Python script: /home/seann/scratch/denoise/fmriprep-denoise-benchmark/fmriprep_denoise/features/build_features_test_parallelized.py
#    - Input directory: /home/seann/scratch/halfpipe_test/test15/derivatives/denoise_0.8subjectthreshold
#    - Output directory: /home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-4.27.25_parallelTest
# 3. Confirm the virtual environment is correctly set up and activated:
#    - Path: /home/seann/scratch/denoise/fmriprep-denoise-benchmark/denoise/bin/activate
# 4. Verify the dataset, fmriprep version, atlas, dimension, and QC parameters:
#    - Dataset: ds000228
#    - fmriprep version: fmriprep-20.2.7
#    - Atlas: Schaefer2018
#    - Dimension: 426
#    - QC: minimal
# 5. Confirm the number of strategies (N_STRATS) matches the HALFpipe runs:
#    - Current value: 7
# 6. Ensure the metrics array is correctly defined:
#    - Current metrics: connectome, qcfc, modularity
# 7. Check SLURM job settings (e.g., time, memory, CPUs, and array range).
# 8. Verify the log file paths for SLURM output and error logs:
#    - Output: /home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/generate_metrics/slurm/logs/parallelized.%a.out
#    - Error: /home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/generate_metrics/slurm/logs/parallelized.%a.err
###############################################################################