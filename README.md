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

   
```bash
git clone --recurse-submodules https://github.com/SIMEXP/fmriprep-denoise-benchmark.git
cd fmriprep-denoise-benchmark
virtualenv env
source env/bin/activate
pip install -r binder/requirements.txt
pip install .
make data
make book
```

<pre><code class="language-python">
```python
from fmriprep_denoise.pipeline import run_denoising_pipeline

# Example: Run denoising on HALFpipe output for a single subject
run_denoising_pipeline(
    input_dir="/path/to/HALFpipe/output",
    subject_id="sub-001",
    strategy="compcor"
)
```
</code></pre>

## Dataset structure

- `binder/` contains files to configure for neurolibre and/or binder hub.

- `content/` is the source of the JupyterBook.

- `data/` is reserved to store data for running analysis.
  To build the book, one will need all the metrics from the study.
  The metrics are here:
  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7764979.svg)](https://doi.org/10.5281/zenodo.7764979)
  The data will be automatically downloaded to `content/notebooks/data`.
  You can by pass this step through accessing the Neurolibre preprint [![DOI](https://neurolibre.org/papers/10.55458/neurolibre.00012/status.svg)](https://doi.org/10.55458/neurolibre.00012)!

- Custom code is located in `fmriprep_denoise/`. This project is installable.

- Preprocessing SLURM scripts, and scripts for creating figure for manuscript are in `scripts/`.

## Quick Start
## Step 1: Generate Outputs from HALFpipe

This workflow has been written to accept derivative files from HALFpipe. Before running this code, please ensure you have run HALFpipe on your dataset successfully with all your desired denoising strategies. 

For those new to HALFpipe, here is the user manual provided by the Enigma Resting State group. Included are step-by-step instructions on how to generate atlas-based connectivity matrices for the Enigma-recommended denoising strategies. [Enigma HALFpipe resting state manual](https://docs.google.com/document/d/1yVVlco4DYr3PwF5L74A5bJB2ivTMwjOV/edit?usp=sharing&ouid=105893466143665916946&rtpof=true&sd=true)


## Step 2: Run slurm_transition_timeseries.sh

We will now begin running the workflow on HALFpipe outputs. 

First, we must convert the HALFpipe generated timeseries matrices into the format expected by our denoising workflow by running the slurm_transition_timeseries.sh script. 

Required for inputs: Please adjust these flags passed to the function call in the slurm_transition_timeseries.sh script. 
1. --input_dir  /path/to/your/halfpipe/derivatives
2. --output_dir /path/to/your/halfpipe/derivatives/denoise
3. --task <place name of your task here> (eg. pixar for sub-pixar001_task-pixar_feature-corrMatrix_atlas-schaefer400_timeseries.tsv)
4. --space <place name of your template space> (eg. MNI152NLin2009cAsym for sub-pixar001_task-pixar_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz)
5. --nroi <place number of ROIs in your atlas> (eg. 434 for atlas-Schaefer2018Combined_dseg.nii.gz)
6. --atlas /path/to/your/atlas.tsv (eg. /atlas/atlas_enigma/atlas-Schaefer2018Combined_dseg.tsv)
7. --nan_threshold <place desired cut off threshold for excluding ROIs> (eg. default set to 0.5)

Please adjust this before running:
1. In the /fmriprep-denoise-benchmark/scripts/halfpipe_to_denoise/transition_timeseries_imputation.py file, please adjust the FEATURE_RENAME_MAP to reflect the naming of your denoising strategies.
eg. If you ran HALFpipe from the user manual, your FEATURE_RENAME_MAP should be adjusted to this:
- FEATURE_RENAME_MAP = {
    "corrMatrix1": "compcor",
    "corrMatrix3": "scrubbing.5+gsr",
    "corrMatrix2": "scrubbing.5",
}

Please adjust the SBATCH flags to reflect your account/allocation at the top of the slurm_transition_timeseries.sh script.

Once finished, you can run the slurm script from the /scripts/halfpipe_to_denois directory by running: SBATCH slurm_transition_timeseries.sh 


## Step 3: Run slurm_meta_confounds.sh

We must now generated the confounds_phenotype.tsv and movement_phenotype.tsv files for our dataset.

NOTE: Correct calculation of degrees of freedom loss for certain denoising strategies require specific files. Some versions of HALFpipe may not provide all necessary files, but future versions will address this.
- Scrubbing strategies requires _res-2_desc-preproc_bold.nii.gz subject files from fmriprep derivatives (sometimes already outputted by HALFpipe)
- Aroma strategies require _desc-aroma_timeseries.tsv subject files from HALFpipe derivatives (outputted with HALFpipe 1.2.3dev).

Required for inputs: Please adjust these flags passed to the function call in the slurm_meta_confounds.sh script.
1. output path: /path/to/outputs/denoise-metrics/dataset/fmriprep-version (eg. /path/to/outputs/denoise-metrics-atlas.5-5.08.25/ds000228/fmriprep-25.0.0)
2. --fmriprep_path= /path/to/your/halfpipe/derivatives/fmriprep 
3. --dataset_name=<place dataset name here> (eg. ds000228)
4. --specifier=<place specifier here> (eg. task-pixar for sub-pixar001_task-pixar_desc-confounds_timeseries.tsv in fmriprep derivatives folder)
5. --participants_tsv /path/to/your/dataset/participants.tsv

Please also ensure that benchmark_strategies.json contains all the denoising strategies you desire to test. 

## Step 4: Run metrics_heavy_resource_parallelized.sh

We can now generate the denoising benchmark metrics for each strategy. 

This script will calculate connectome, modularity, and QCFC metrics for all denoising strategies 

Required for inputs: 



## Step 5: Run slurm_summarise_metadata.sh

We can now generate the summary.tsv file for our metrics and selected quality control (QC) level.

Required for inputs:


## Step 6: Run slurm_make_manuscript_figures.sh

We can now generate figures to visualize our metrics. 

Required for inputs:



