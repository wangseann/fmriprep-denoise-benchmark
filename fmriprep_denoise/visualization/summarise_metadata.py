"""
Summarise data for visualisation.
To retrievel atlas information, you need internet connection.
"""
import argparse
from pathlib import Path
import pandas as pd
from fmriprep_denoise.features.derivatives import get_qc_criteria
from fmriprep_denoise.visualization import utils


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Summarise denoising metrics for visualization and save at the top level of the denoise metric outputs directory.",
    )
    parser.add_argument(
        "output_root", action="store", default=None, help="Output root path data."
    )
    parser.add_argument(
        "--fmriprep_version",
        action="store",
        type=str,
        help="Path to a fmriprep dataset.",
    )
    parser.add_argument(
        "--dataset_name",
        action="store",
        type=str,
        help="Dataset name.",
    )
    parser.add_argument(
        "--qc",
        action="store",
        default=None,
        help="Automatic motion QC thresholds.",
    )
    return parser.parse_args()


def run(output_root: str, fmriprep_version: str, dataset_name: str, qc: str, derivatives_root: str):
    print(f"Arguments passed: {{'output_root': output_root, 'fmriprep_version': fmriprep_version, 'dataset_name': dataset_name, 'qc': qc, 'derivatives_root': derivatives_root}}")
    input_root = (
        utils.get_data_root() / "denoise-metrics"
        if output_root is None
        else Path(output_root)
    )
    output_root_path = (
        utils.get_data_root() / "denoise-metrics"
        if output_root is None
        else Path(output_root)
    )
    qc_name = qc
    dataset = dataset_name
    fmriprep_version_local = fmriprep_version

    qc_criteria = get_qc_criteria(qc_name)
    if qc_name is None:
        qc_name = "None"

    print(f"Processing {dataset}, {qc_name}, {fmriprep_version_local}...")
    ds_modularity = utils.prepare_modularity_plotting(
        dataset, fmriprep_version_local, None, None, input_root, qc_criteria
    )

    excluded_rois_path = Path(derivatives_root) / "denoise" / "rois_dropped.csv"
    ds_qcfc = utils.prepare_qcfc_plotting(
        dataset, fmriprep_version_local, None, None, input_root, excluded_rois_path
    )

    data = pd.concat([ds_qcfc, ds_modularity], axis=1)
    filename = f"{dataset}_{fmriprep_version_local.replace('.', '-')}_desc-{qc_name}_summary.tsv"
    output_path = output_root_path / dataset / fmriprep_version_local / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, sep="\t")


if __name__ == "__main__":
    args = parse_args()
    run(
        output_root=args.output_root,
        fmriprep_version=args.fmriprep_version,
        dataset_name=args.dataset_name,
        qc=args.qc,
        derivatives_root=None,
    )
