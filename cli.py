#!/usr/bin/env python3

import argparse
import logging
from scripts.halfpipe_to_denoise import transition_timeseries_imputation
from fmriprep_denoise.features import calculate_degrees_of_freedom_test_noboldpreproc_aromafix as calculate_dof
from fmriprep_denoise.features import build_features_test_parallelized as features
from fmriprep_denoise.visualization import summarise_metadata


def main():
    parser = argparse.ArgumentParser(
        description="BIDS App CLI for fMRIPrep-denoise-benchmark."
    )

    # Required BIDS App positional arguments
    parser.add_argument("bids_dir", help="BIDS dataset directory (or derivatives root).")
    parser.add_argument("output_dir", help="Output directory for all derivative outputs.")
    parser.add_argument("analysis_level", choices=["participant", "group"],
                        help="Level of analysis that is to be performed.")

    # Shared optional flags
    parser.add_argument("--participant-label", nargs="+",
                        help="Optional list of participant labels to process (e.g., sub-01 sub-02)")

    # Step selection
    parser.add_argument("--step", required=True,
                        choices=["impute", "dof", "features", "summarise"],
                        help="Pipeline step to run.")

    # impute-specific options
    parser.add_argument("--task", default="pixar", help="Task label (default: pixar)")
    parser.add_argument("--space", default="MNI152NLin2009cAsym", help="Template space")
    parser.add_argument("--nroi", type=int, required=True, help="Number of ROIs")
    parser.add_argument("--atlas", type=str, required=True, help="Path to atlas TSV file")
    parser.add_argument("--nan-threshold", type=float, default=0.5,
                        help="Threshold for ROI-wise NaN exclusion (default: 0.5)")
    
    # DOF-specific options
    parser.add_argument("--dataset-name", type=str, help="Dataset name (used in output filename).")
    parser.add_argument("--specifier", type=str, help="Specifier (e.g., 'task-pixar') for confound filenames.")
 

    # features-specific options
    parser.add_argument("--atlas", type=str, help="Atlas name (e.g., schaefer400, mist)")
    parser.add_argument("--dimension", type=str, help="Number of ROIs in the atlas")
    parser.add_argument("--qc", type=str, default=None, help="QC thresholding (e.g., stringent, minimal)")
    parser.add_argument("--metric", type=str, default="connectomes", help="Metric to compute: connectome, qcfc, modularity, or all")
    parser.add_argument("--strategy_index", type=int, default=None, help="Index of strategy to run")
    parser.add_argument("--dataset-name", type=str, help="Dataset name override")
    parser.add_argument("--fmriprep_ver", type=str, help="fMRIPrep version override")

    # summarise-specific options
    parser.add_argument("--dataset-name", type=str, help="Dataset name override")
    parser.add_argument("--fmriprep_version", type=str, help="fMRIPrep version string (e.g., fmriprep-25.0.0)")
    parser.add_argument("--qc", type=str, help="QC threshold name (e.g., stringent, minimal)")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    if args.step == "impute":
        transition_timeseries_imputation.run(
            input_dir=args.bids_dir,
            output_dir=args.output_dir,
            task=args.task,
            space=args.space,
            nroi=args.nroi,
            atlas=args.atlas,
            nan_threshold=args.nan_threshold
        )
    elif args.step == "dof":
        calculate_dof.run(
            output_path=args.output_dir,
            fmriprep_path=args.bids_dir,
            dataset_name=args.dataset_name,
            specifier=args.specifier,
            participants_tsv=args.participants_tsv
        )
    elif args.step == "features":
        features.run(
            input_path=args.bids_dir,
            output_path=args.output_dir,
            atlas=args.atlas,
            dimension=args.dimension,
            qc=args.qc,
            metric=args.metric,
            strategy_index=args.strategy_index,
            dataset=args.dataset_name,
            fmriprep_ver=args.fmriprep_ver,
        )
    elif args.step == "summarise":
        summarise_metadata.run(
            output_root=args.output_dir,
            fmriprep_version=args.fmriprep_version,
            dataset_name=args.dataset_name,
            qc=args.qc,
            derivatives_root=args.bids_dir
        )

if __name__ == "__main__":
    main()