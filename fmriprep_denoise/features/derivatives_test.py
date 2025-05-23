import json
import tarfile
from pathlib import Path
import pandas as pd
from nilearn.connectome import ConnectivityMeasure
from sklearn.impute import SimpleImputer
import numpy as np
from fmriprep_denoise.visualization import tables


MOTION_QC_FILE = "motion_qc.json"
project_root = Path(__file__).parents[2]
inputs = project_root / "data"
group_info_column = {"ds000228": "Child_Adult", "ds000030": "diagnosis"}


def get_qc_criteria(strategy_name=None):
    """
    Select an automatic quality control strategy and associated parameters.

    Parameter
    ---------

    strategy_name : None or str
        Name of the denoising strategy. See motion_qc.json.
        Default to None, returns all strategies.

    Return
    ------

    dict
        Motion quality control parameter to pass to filter subjects.
    """
    motion_qc_file = Path(__file__).parent / MOTION_QC_FILE
    with open(motion_qc_file, "r") as file:
        qc_strategies = json.load(file)

    if isinstance(strategy_name, str) and strategy_name not in qc_strategies:
        raise NotImplementedError(
            f"Strategy '{strategy_name}' is not implemented. Select from the"
            f"following: None, {[*qc_strategies]}"
        )

    if strategy_name is None:
        print("No motion QC.")
        return {"gross_fd": None, "fd_thresh": None, "proportion_thresh": None}
    (f"Process strategy '{strategy_name}'.")
    return qc_strategies[strategy_name]


def compute_connectome(
    atlas,
    extracted_path,
    dataset,
    fmriprep_version,
    path_root,
    file_pattern,
    full_roi_list,  # added to grab roi list from atlas tsv
    gross_fd=None,
    fd_thresh=None,
    proportion_thresh=None,
):
    """Compute connectome of all valid data.

    Parameters
    ----------
    atlas : str
        Atlas name matching keys in fmriprep_denoise.dataset.atlas.ATLAS_METADATA.
    extracted_path : pathlib.Path
        Path object to where the time series were saved.
    dataset : str
        Name of the dataset.
    fmriprep_version : str {fmrieprep-20.2.1lts, fmrieprep-20.2.5lts}
        fMRIPrep version used for preporcessin.
    file_pattern : str
        Details about the atlas and description of the file.
    full_roi_list : list
        List of regions of interest from the atlas TSV file.
    gross_fd : optional
        Framewise displacement values (optional).
    fd_thresh : optional
        Threshold for FD (optional).
    proportion_thresh : optional
        Threshold for proportion (optional).

    Returns
    -------
    pandas.DataFrame, pandas.DataFrame
        Flatten connectomes and phenotypes.
    """
    _, phenotype, _ = tables.get_descriptive_data(
        dataset, fmriprep_version, path_root, gross_fd, fd_thresh, proportion_thresh
    )
    participant_id = phenotype.index.tolist()
    valid_ids, valid_ts = _load_valid_timeseries(
        atlas, extracted_path, participant_id, file_pattern, full_roi_list  # pass rois 
    )

    # Print the number of time series loaded
    print(f"Number of time series loaded: {len(valid_ts)}")
    if len(valid_ts) == 0:
        print(f"Matching file pattern was: {file_pattern}")
    
    # Compute connectivity using the correlation measure
    correlation_measure = ConnectivityMeasure(
        kind="correlation", vectorize=True, discard_diagonal=True
    )
    subject_conn = correlation_measure.fit_transform(valid_ts)
    subject_conn = pd.DataFrame(subject_conn, index=valid_ids)
    
    if subject_conn.shape[0] != phenotype.shape[0]:
        print("Taking conjunction of the phenotype and connectome.")
        idx = subject_conn.index.intersection(phenotype.index)
        subject_conn, phenotype = (
            subject_conn.loc[idx, :],
            phenotype.loc[idx, :],
        )
    
    return subject_conn, phenotype


def check_extraction(input_path, extracted_path_root=None):
    """Check if the tar.gz of a fmriprep dataset has been extracted.

    Parameters
    ----------

    input_path : pathlib.Path
        Location of the tar.gz of the fMRIPrep output.

    extracted_path_root : None, pathlib.Path
        Destination of the extraction.

    Returns
    -------

    pathlib.Path
        Correct file path of the extracted dataset.
    """
    dir_name = input_path.name.split(".tar")[0]
    extracted_path_root = inputs if extracted_path_root is None else extracted_path_root

    extracted_path = extracted_path_root / dir_name

    if not extracted_path.is_dir() and input_path.is_file():
        print(f"Cannot file extracted file at {extracted_path}. " "Extracting...")
        with tarfile.open(input_path, "r:gz") as tar:
            tar.extractall(extracted_path_root)
    return extracted_path


def _load_valid_timeseries(atlas, extracted_path, participant_id, file_pattern, full_roi_list):
    """Load time series from tsv file and align the columns to the full ROI list."""
    valid_ids, valid_ts = [], []
    for subject in participant_id:
        subject_path = extracted_path / subject  # <-- FIXED
        file_path = list(
            subject_path.glob(f"{subject}_*_{file_pattern}_timeseries.tsv")
        )
        print("Load_valid_timeseries from: " + str(file_path))
        if len(file_path) > 1:
            raise ValueError("Found more than one valid file: " + str(file_path))
        if not file_path:
            continue
        file_path = file_path[0]
        if file_path.stat().st_size > 1:
            df = pd.read_csv(file_path, sep="\t", header=None)
            df.columns = full_roi_list
            valid_ids.append(subject)
            valid_ts.append(df.values)
        else:
            continue
    return valid_ids, valid_ts

def load_full_roi_list(atlas_tsv_path):
    """
    Load the full list of expected ROI names from an atlas TSV file.
    Assumes the ROI names are in the second column.
    """
    atlas_df = pd.read_csv(atlas_tsv_path, sep="\t", header=None)
    full_roi_list = atlas_df[1].tolist()
    return full_roi_list
