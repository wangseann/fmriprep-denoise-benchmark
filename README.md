#**Update Feburary 2025**
This project is a continuation of **Benchmark denoising strategies on fMRIPrep output**. 
The aim is to adapt the original denoising workflow to utilize HALFpipe outputs.

<img width="561" alt="Screenshot 2025-04-30 at 10 30 14 PM" src="https://github.com/user-attachments/assets/5a848bf7-c2ee-4395-ae5d-c13ef543c5e5" />



# Benchmark denoising strategies on fMRIPrep output

[![DOI](https://neurolibre.org/papers/10.55458/neurolibre.00012/status.svg)](https://doi.org/10.55458/neurolibre.00012)

The project is a continuation of [load_confounds](https://github.com/SIMEXP/load_confounds) and [fmriprep-denoise-benchmark](https://github.com/SIMEXP/fmriprep-denoise-benchmark).

The aim is to evaluate the impact of denoising strategy on functional connectivity data, using output processed by HALFpipe in a reproducible workflow.


## Recommandations for those who thought this project is a software

The code in this repository reflects the research done for the manuscript, and is not suitable for production level application. (yet)

Some useful part of the code has been extracted and further reviewed within SIMEXP lab for deplyment on generic fmriprep derivatives as docker images.

 - *time series and connectome workflow*: [`giga_connectome`](https://github.com/SIMEXP/giga_connectome).
 - *motion quality control metrics*: [`giga_auto_qc`](https://github.com/SIMEXP/giga_auto_qc).

## Quick start
1. Generate Outputs from HALFpipe
2. Run slurm_transition_timeseries.sh
3. Run slurm_meta_confounds.sh
4. Run metrics_heavy_resource_parallelized.sh
5. Run slurm_summarise_metadata.sh
6. Run slurm_make_manuscript_figures.sh

<pre><code>

</code></pre>


## Dataset structure

- Custom code is located in `fmriprep_denoise/`. This project is installable.

- Preprocessing SLURM scripts, and scripts for creating figure for manuscript are in `scripts/`.


## Step 1: Generate Outputs from HALFpipe

This workflow has been written to accept derivative files from HALFpipe. Before running this code, please ensure you have run HALFpipe on your dataset successfully with all your desired denoising strategies. 

For those new to HALFpipe, here is the user manual provided by the Enigma Resting State group. Included are step-by-step instructions on how to generate atlas-based connectivity matrices for the Enigma-recommended denoising strategies. [Enigma HALFpipe resting state manual](https://docs.google.com/document/d/1yVVlco4DYr3PwF5L74A5bJB2ivTMwjOV/edit?usp=sharing&ouid=105893466143665916946&rtpof=true&sd=true)


## Step 2: Run slurm_transition_timeseries.sh

We will now begin running the workflow on HALFpipe outputs. 

First, we must convert the HALFpipe generated timeseries matrices into the format expected by our denoising workflow by running the slurm_transition_timeseries.sh script. 


Required for inputs: Please adjust these flags passed to the function call in the slurm_transition_timeseries.sh script. 

<pre><code>
1. --input_dir  /path/to/your/halfpipe/derivatives

2. --output_dir /path/to/your/halfpipe/derivatives/denoise
   
4. --task <place name of your task here> (eg. pixar for sub-pixar001_task-pixar_feature-corrMatrix_atlas-schaefer400_timeseries.tsv)
   
5. --space <place name of your template space> (eg. MNI152NLin2009cAsym for sub-pixar001_task-pixar_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz)
   
6. --nroi <place number of ROIs in your atlas> (eg. 434 for atlas-Schaefer2018Combined_dseg.nii.gz)
   
7. --atlas /path/to/your/atlas.tsv (eg. /atlas/atlas_enigma/atlas-Schaefer2018Combined_dseg.tsv)
   
8. --nan_threshold <place desired cut off threshold for excluding ROIs> (eg. default set to 0.5)
</code></pre>

Please adjust this before running:
1. In the /fmriprep-denoise-benchmark/scripts/halfpipe_to_denoise/transition_timeseries_imputation.py file, please adjust the FEATURE_RENAME_MAP to reflect the naming of your denoising strategies.
eg. If you ran HALFpipe from the user manual, your FEATURE_RENAME_MAP should be adjusted to this:
<pre><code>
FEATURE_RENAME_MAP = {
    "corrMatrix1": "compcor",
    "corrMatrix3": "scrubbing.5+gsr",
    "corrMatrix2": "scrubbing.5",
}
</code></pre>

Please adjust the SBATCH flags to reflect your account/allocation at the top of the slurm_transition_timeseries.sh script.

Once finished, you can run the slurm script from the /scripts/halfpipe_to_denois directory by running: SBATCH slurm_transition_timeseries.sh 


## Step 3: Run slurm_meta_confounds.sh

We must now generated the confounds_phenotype.tsv and movement_phenotype.tsv files for our dataset.

NOTE: Correct calculation of degrees of freedom loss for certain denoising strategies require specific files. Some versions of HALFpipe may not provide all necessary files, but future versions will address this.
- Scrubbing strategies requires _res-2_desc-preproc_bold.nii.gz subject files from fmriprep derivatives (sometimes already outputted by HALFpipe)
- Aroma strategies require _desc-aroma_timeseries.tsv subject files from HALFpipe derivatives (outputted with HALFpipe 1.2.3dev).

Required for inputs: Please adjust these flags passed to the function call in the slurm_meta_confounds.sh script.
<pre><code>
1. output path: /path/to/outputs/denoise-metrics/dataset/fmriprep-version (eg. /path/to/outputs/denoise-metrics-atlas.5-5.08.25/ds000228/fmriprep-25.0.0)
 
2. --fmriprep_path= /path/to/your/halfpipe/derivatives/fmriprep 
 
3. --dataset_name=<place dataset name here> (eg. ds000228)
 
4. --specifier=<place specifier here> (eg. task-pixar for sub-pixar001_task-pixar_desc-confounds_timeseries.tsv in fmriprep derivatives folder)
 
5. --participants_tsv /path/to/your/dataset/participants.tsv
</code></pre>

Please also ensure that benchmark_strategies.json contains all the denoising strategies you desire to test. 

## Step 4: Run metrics_heavy_resource_parallelized.sh

We can now generate the denoising benchmark metrics for each strategy. 

This script will calculate connectome, modularity, and QCFC metrics for all denoising strategies 

Required for inputs: 

In the slurm script:
<pre><code>
N_STRATS = <place number of denoising strategies that you ran here> (eg. 3 if running from HALFpipe manual, can be higher like 9)

SBATCH --array=<place 0 - (N_STRATS*METRICS)-1 here> (eg. 9 x 3 = 27, array = 0-26)
</code></pre>
In the python function call:
<pre><code>
1. Please adjust python script path for your codebase.
2. Please adjust denoising timeseries folder path for your codebase (eg. /path/to/your/halfpipe/derivatives/denoise
3. Please adjust your output path (eg. /path/to/outputs/denoise-metrics)
4. --dataset <place dataset name here> (eg. ds000228)
5. --fmriprep_ver <place fmriprep version here> (eg. fmriprep-20.2.7)
6. --atlas <place atlas name here> (eg. schaefer400)
7. --dimension <place number of rois here> (eg. you can find this as the number of rows minus 1 in the final_roi_label.csv file found in /path/to/your/halfpipe/derivatives/denoise)
8. --qc <place desired QC level here> (eg. minimal or stringent or None)
</code></pre>



## Step 5: Run slurm_summarise_metadata.sh

We can now generate the summary.tsv file for our metrics and selected quality control (QC) level.

1. INSIDE /path/to/fmriprep_denoise/visualization/summarise_metadata.py, please adjust the following. 

#hardcoded in summarise_metadata.py
<pre><code>
qc_names = ["stringent"] #adjust for your QC level
datasets = ["ds000228"] #adjust for your dataset name
fmriprep_versions = ["fmriprep-20.2.7"] #adjust for your fmriprep version

</code></pre>

2. INSIDE /path/to/fmriprep_denoise/visualization/utils.py, please adjust the following. 

#please ensure these strategies match those found in benchmark_strategies.json
<pre><code>
GRID_LOCATION = { 
    (0, 0): "baseline",
    (0, 2): "simple",
    (0, 3): "simple+gsr",
    (1, 0): "simple+wmcsf",
    (1, 1): "scrubbing.5",
    (1, 2): "scrubbing.5+gsr",
    (1, 3): "scrubbing.5+wmcsf",
    (2, 0): "compcor",
    (2, 1): "aroma",
}
</code></pre>
#hardcoded in utils.py
Please adjust these paths to point to your own rois_dropped.csv in the /deriatives/denoise folder. Its okay to only have one path if only testing 1 version.
<pre><code>
excluded_rois_paths = {
    "fmriprep-25.0.0": "/home/seann/scratch/halfpipe_test/25-04-25_ds228_halfpipe-1.2.3_fmriprep-25.0.0_dvars-corrected/derivatives/denoise/rois_dropped.csv", 
    "fmriprep-20.2.7": "/home/seann/scratch/halfpipe_test/25-04-17_ds228_halfpipe-1.2.3_fmriprep-20.2.7/derivatives/denoise/rois_dropped.csv",
}
</code></pre>

3. Required for inputs:
   
<pre><code>
1. input path: /path/to/your/outputs/denoise-metrics
2. --fmriprep_version <place fmriprep version here> (eg. fmriprep-20.2.7)
</code></pre>
3. --dataset_name <place dataset name here> (eg. ds000228)
4. --qc <place desired QC level here> (eg. minimal or stringent or None)
</code></pre>


## Step 6: Run slurm_make_manuscript_figures.sh

We can now generate figures to visualize our metrics. 

1. INSIDE /path/to/scripts/make_manuscript_figures.py
#please adjust these hardcoded settings for your workflow
<pre><code>
group_order = {
    "ds000228": ["adult", "child"]
}
datasets = ["ds000228"]
datasets_baseline = {"ds000228": "adult"}
criteria_name = "stringent"
fmriprep_version = "fmriprep-25.0.0"
excluded_strategies = []#["compcor", "aroma"]
</code></pre>

#please adjust path_root to /path/to/your/outputs/denoise-metrics
<pre><code>
if __name__ == "__main__":
  path_root = Path("/home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-5.08.25") 
 
</code></pre>

#please adjust the strategy_order to match your strategy names
<pre><code>
strategy_order = ["scrubbing.5+gsr","simple+gsr","compcor","scrubbing.5","simple","aroma","baseline"]

</code></pre>


#You should now have generated the manuscript figures for the denoising benchmark metrics in /path/to/your/outputs. 

