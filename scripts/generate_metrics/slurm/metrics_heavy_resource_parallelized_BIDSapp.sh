#!/bin/bash
#SBATCH --job-name=lts_metrics_%A_%a
#SBATCH --account=def-cmoreau
#SBATCH --time=15:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --array=0-26
#SBATCH --output=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/generate_metrics/slurm/logs/parallelized_bidsapp.%a.out
#SBATCH --error=/home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/generate_metrics/slurm/logs/parallelized_bidsapp.%a.err

set -euo pipefail

module load apptainer

N_STRATS=9
METRICS=(connectome qcfc modularity)

flat=$SLURM_ARRAY_TASK_ID
METRIC=${METRICS[$((flat / N_STRATS))]}
STRAT_INDEX=$((flat % N_STRATS))

echo "Task $flat  metric=$METRIC  strategy_index=$STRAT_INDEX"

apptainer run \
  -B /home/seann/scratch:/scratch \
  /home/seann/scratch/denoise/fmriprep-denoise-benchmark/fmriprep-denoise-benchmark.sif \
  /scratch/halfpipe_test/25-04-17_ds228_halfpipe-1.2.3_fmriprep-20.2.7/derivatives/denoise \
  /scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-5.08.25 \
  participant \
  --step features \
  --dataset ds000228 \
  --fmriprep_ver fmriprep-20.2.7 \
  --atlas schaefer400 \
  --dimension 426 \
  --qc stringent \
  --metric "$METRIC" \
  --strategy_index "$STRAT_INDEX"