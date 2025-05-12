#!/bin/bash
# Get some confounds metadata, such as the number of volumes scrubbed
# Run after generating the fMRIPrep dataset

#SBATCH --job-name=visualize_final_shape
#SBATCH --time=1:00:00
#SBATCH --account=def-cmoreau
#SBATCH --output=logs/visualize_final_shape.out
#SBATCH --error=logs/visualize_final_shape.err
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G 

# Activate the Python virtual environment.
source /home/seann/scratch/denoise/fmriprep-denoise-benchmark/denoise/bin/activate

# Change to the directory containing the visualization script.
cd /home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/halfpipe_to_denoise

# Run the visualization script with all required arguments.
python visualize_final_shape.py \
    --atlas_img /home/seann/projects/def-cmoreau/All_user_common_folder/atlas/atlas_enigma/atlas-Schaefer2018Combined_dseg.nii.gz \
    --atlas_tsv /home/seann/projects/def-cmoreau/All_user_common_folder/atlas/atlas_enigma/atlas-Schaefer2018Combined_dseg.tsv \
    --exclusion_csv /home/seann/scratch/halfpipe_test/25-04-25_ds228_halfpipe-1.2.3_fmriprep-25.0.0_dvars-corrected/derivatives/denoise/final_roi_labels.csv \
    --global_impute_csv /home/seann/scratch/halfpipe_test/25-04-25_ds228_halfpipe-1.2.3_fmriprep-25.0.0_dvars-corrected/derivatives/denoise/roi_global_impute_counts.csv \
    --output /home/seann/scratch/denoise/fmriprep-denoise-benchmark/scripts/halfpipe_to_denoise/visualize_rois_1.2.3dev.png \
    --title "Final ROIs for 1.2.3dev DVARS-corrected" \