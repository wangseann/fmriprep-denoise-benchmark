
"""
Fast vectorised QC‑FC routine that preserves the *original* API.

Public symbols (unchanged):
    • calculate_qcfc(data_frame, connectivity_matrices, metric_key="MeanFramewiseDisplacement")
    • qcfc  (alias to the same function, because the old __all__ listed it)
    • calculate_median_absolute
    • significant_level
    • partial_correlation  (re‑exported from the legacy module)

Returned dataframe:
    MultiIndex ["i","j"] on the rows, with columns ["correlation","p_value"],
    identical to the previous implementation.
"""
from __future__ import annotations

from itertools import chain
from typing import Iterable

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from patsy.highlevel import dmatrix
from scipy import stats, linalg
from tqdm.auto import tqdm

# re‑export to keep backwards compatibility with external imports
from ..correlation import correlation_p_value, partial_correlation  # noqa: F401
from ..base import ConnectivityMatrix

__all__ = [
    "calculate_median_absolute",
    "significant_level",
    "partial_correlation",
    "calculate_qcfc",
    "qcfc",  # alias – some code used this name
]

# ---------------------------------------------------------------------
# small helpers (unchanged behaviour)
def calculate_median_absolute(x: pd.Series) -> float:
    """Absolute median value."""
    return x.abs().median()


def significant_level(
    x: pd.Series,
    alpha: float = 0.05,
    correction: str | None = None,
) -> NDArray[np.bool_]:
    """FDR correction helper (unchanged)."""
    from statsmodels.stats import multitest

    if isinstance(correction, str):
        res, *_ = multitest.multipletests(x, alpha=alpha, method=correction)
    else:
        res = x < alpha
    return res


# ---------------------------------------------------------------------
# internal maths
def _regress_out(cov: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Return residuals of *y* after linear regression on *cov*."""
    betas, *_ = linalg.lstsq(cov, y, rcond=None)
    return y - cov @ betas


# ---------------------------------------------------------------------
def calculate_qcfc(
    data_frame: pd.DataFrame,
    connectivity_matrices: Iterable[ConnectivityMatrix],
    metric_key: str = "MeanFramewiseDisplacement",
) -> pd.DataFrame:
    """
    Drop‑in replacement for the original (loop‑based) QC‑FC.

    Parameters
    ----------
    data_frame
        Must contain columns “age” and “gender” with one row per subject.
    connectivity_matrices
        Iterable of `ConnectivityMatrix` objects, same order as *data_frame*.
    metric_key
        Motion metric inside each matrix’s `.metadata` (default “MeanFramewiseDisplacement”).

    Returns
    -------
    pd.DataFrame
        MultiIndex ["i","j"] rows, columns = ["correlation", "p_value"].
    """
    # ------------------------------------------------------------------
    # Materialise the iterable (we need it twice)
    matrices = list(connectivity_matrices)
    if not matrices:
        raise ValueError("No connectivity matrices provided.")

    n_subjects = len(matrices)

    # ---------------- Motion metric -----------------------------------
    motion = np.asarray(
        [m.metadata.get(metric_key, np.nan) for m in matrices], dtype=float
    )

    # ---------------- Covariates (age + gender) -----------------------
    # patsy adds an intercept automatically, matching the original code
    cov = np.asarray(dmatrix("age + gender", data_frame), dtype=float)

    # ---------------- Connectivity edges ------------------------------
    # get edge indices from the first matrix
    first_arr = matrices[0].load()
    (n_nodes,) = {dim for a in (first_arr,)}

    i_idx, j_idx = np.tril_indices(n_nodes, k=-1)
    n_edges = len(i_idx)

    X = np.empty((n_subjects, n_edges), dtype=float)  # shape (subjects, edges)

    for s, m in enumerate(tqdm(matrices, desc="Loading connectivity matrices", leave=False)):
        arr = m.load()
        # quick sanity check
        if arr.shape != (n_nodes, n_nodes):
            raise ValueError("All connectivity matrices must be square and the same size.")
        X[s, :] = arr[i_idx, j_idx]

    # ---------------- Vectorised QC‑FC -------------------------------
    # Z‑score covariates to improve conditioning
    if cov.size:
        C = stats.zscore(cov, nan_policy="omit")
        X = _regress_out(C, X)                  # residuals of each edge
        y = _regress_out(C, motion[:, None]).ravel()
        dof = n_subjects - C.shape[1] - 2       # degrees of freedom
    else:
        y = motion
        dof = n_subjects - 2

    # Pearson r and two‑tailed p (vectorised)
    xy = np.einsum("ij,i->j", X, y)
    xx = np.einsum("ij,ij->j", X, X)
    yy = np.dot(y, y)

    r = xy / np.sqrt(xx * yy)
    r = np.clip(r, -1.0, 1.0)                   # numerical stability

    t = r * np.sqrt(dof / (1.0 - r**2))
    p = 2.0 * stats.t.sf(np.abs(t), dof)

    # ---------------- Assemble output -------------------------------
    qcfc_df = pd.DataFrame(
        {
            "correlation": r,
            "p_value": p,
        },
        index=pd.MultiIndex.from_arrays([i_idx, j_idx], names=("i", "j")),
    )

    return qcfc_df


# Many call‑sites imported `qcfc`; keep it as an alias.
def qcfc(*args, **kwargs):
    return calculate_qcfc(*args, **kwargs)