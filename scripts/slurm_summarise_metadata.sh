#!/bin/bash
# Get some confounds metadata, such as numver of volumes scrubbed
# Run after generating fMRIPRep dataset
#SBATCH --job-name=summarise_metadata
#SBATCH --time=1:00:00
#SBATCH --account=def-cmoreau
#SBATCH --output=logs/summarise_metadata_lts.out
#SBATCH --error=logs/summarise_metadata_lts.err
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G 

source /home/seann/scratch/denoise/fmriprep-denoise-benchmark/denoise/bin/activate

cd /home/seann/scratch/denoise/fmriprep-denoise-benchmark/fmriprep_denoise/visualization

python summarise_metadata.py /home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-5.08.25 --fmriprep_version fmriprep-20.2.7 --dataset_name ds000228 --qc stringent


# 
# python summarise_metadata.py /home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-5.08.25 --fmriprep_version fmriprep-25.0.0  --dataset_name ds000228 --qc stringent
