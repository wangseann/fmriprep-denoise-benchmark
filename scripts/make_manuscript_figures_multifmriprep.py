from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
from adjustText import adjust_text
import logging
from fmriprep_denoise.visualization import utils
from fmriprep_denoise.visualization import (
    connectivity_similarity,
    degrees_of_freedom_loss,
    mean_framewise_displacement,
    motion_metrics,
    strategy_ranking,
)

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Settings
fixed_dataset = "ds000228"
datasets = [fixed_dataset]  # Keep as list for function calls
fmriprep_versions = ["fmriprep-20.2.7", "fmriprep-25.0.0"]
criteria_name = "stringent"
excluded_strategies = []

# Paths
path_root = Path("/home/seann/scratch/denoise/fmriprep-denoise-benchmark/outputs/denoise-metrics-atlas.5-5.08.25")
output_dir = Path(__file__).parents[1] / "outputs1"
output_dir.mkdir(parents=True, exist_ok=True)

# Utility
strategy_order = list(utils.GRID_LOCATION.values())
# strategy_order = [s for s in strategy_order if s not in excluded_strategies]
strategy_order = ["scrubbing.5+gsr","simple+gsr","compcor","scrubbing.5","simple","aroma","baseline", "scrubbing.5+wmcsf","simple+wmcsf"]

# Plotting function for Loss vs Quality
def plot_loss_vs_quality(data, output_dir, version_filter):
    sns.set(style="whitegrid", context="talk")

    
    # --- keep ONE .xs() call only -----------------------------
    if version_filter is not None:
        filtered_df = data.xs(version_filter, level="version")
    else:
        filtered_df = data
    # ----------------------------------------------------------

    results = []

    for dataset in filtered_df.index.levels[0]:
        subset = filtered_df.loc[dataset]
        loss_df = subset.loc['loss_df']
        other_metrics = subset.drop('loss_df')

        if isinstance(other_metrics.index, pd.MultiIndex) and "strategy" in other_metrics.index.names:
            strategy_idx = other_metrics.index.get_level_values("strategy")
            other_metrics = other_metrics.loc[~strategy_idx.isin(excluded_strategies)]
        else:
            other_metrics = other_metrics.loc[~other_metrics.index.isin(excluded_strategies)]

        mean_other = other_metrics.mean()
        results.append((dataset, loss_df, mean_other))

    for dataset, loss_df, mean_other in results:
        loss_df = loss_df[[s for s in loss_df.index if (s[1] if isinstance(s, tuple) else s) not in excluded_strategies]]
        mean_other = mean_other[[s for s in mean_other.index if (s[1] if isinstance(s, tuple) else s) not in excluded_strategies]]

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.scatterplot(x=loss_df, y=mean_other, s=100, color="royalblue", ax=ax)

        texts = []
        for strategy in loss_df.index:
            label = strategy[1] if isinstance(strategy, tuple) else strategy
            texts.append(ax.text(loss_df[strategy], mean_other[strategy] + 0.1, label, fontsize=12, ha="center"))

        adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="->", color="gray", lw=0.5))

        ax.set_title(f"{dataset} ({version_filter})\nLoss of DF vs Mean Rank of Other Metrics", fontsize=16)
        ax.set_xlabel("Loss of Degrees of Freedom (Rank)", fontsize=14)
        ax.set_ylabel("Mean Rank of Denoising Quality Metrics", fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.6)
        fig.tight_layout()

        fig.savefig(output_dir / f"{dataset}_loss_vs_quality_{version_filter}.png", transparent=True)
        plt.close(fig)

# MAIN
if __name__ == "__main__":

    # ---------------------------------------------------------------
    #  Collect data once per *version* and plot them side-by-side
    # ---------------------------------------------------------------
    # --- 3a. CONNECTOME SIMILARITY ---------------------------------
    average_connectomes = {
        v: connectivity_similarity
            .load_data(path_root, datasets, v)[fixed_dataset]   # grab the DS-specific DF
        for v in fmriprep_versions
    }

    fig_similarity = connectivity_similarity.plot_stats(
        average_connectomes,                       # keys == versions
        strategy_order=strategy_order,
        show_colorbar=True,
        horizontal=False                           # 1 × 2 layout
    )
    fig_similarity.savefig(output_dir / "connectomes_versions.png", transparent=True)

    # --- 3b. LOSS OF DOF -------------------------------------------
    confounds_versions = {
        v: degrees_of_freedom_loss
            .load_data(path_root, datasets, criteria_name, v)[fixed_dataset]
        for v in fmriprep_versions
    }

    fig_dof = degrees_of_freedom_loss.plot_stats(confounds_versions)
    fig_dof.savefig(output_dir / "loss_degrees_of_freedom_versions.png", transparent=True)

    fig_dof_sub = degrees_of_freedom_loss.plot_stats(
        confounds_versions, plot_subgroup=True
    )
    fig_dof_sub.savefig(output_dir / "loss_degrees_of_freedom_subgroups_versions.png",
                        transparent=True)

    # --- 3c. MOTION METRICS ----------------------------------------
    metrics = {
        "p_values":       "sig_qcfc",
        "fdr_p_values":   "sig_qcfc_fdr",
        "median":         "median_qcfc",
        "distance":       "distance_qcfc",
    }
    for m in metrics:
        mm_versions = {}
        for v in fmriprep_versions:
            data_v, measure = motion_metrics.load_data(
                path_root, datasets, criteria_name, v, m
            )
            df = data_v[fixed_dataset]
            df = df[~df["strategy"].isin(excluded_strategies)]
            mm_versions[v] = df
        fig = motion_metrics.plot_stats(mm_versions, measure)
        fig.savefig(output_dir / f"{metrics[m]}_versions.png", transparent=True)

    # --- 3d.  MODULARITY PAIR (special two-row plot) ---------------
    palette = sns.color_palette("colorblind", n_colors=7)
    paired_palette = [palette[0]]
    for p in palette[1:4]:
        paired_palette.extend((p, p))
    paired_palette.extend((palette[-3], palette[-2], palette[-1], palette[-1]))

    fig_mod = plt.figure(constrained_layout=True, figsize=(6.4, 9.6))
    subfigs_mod = fig_mod.subfigures(2, 1, wspace=0.07)   # 2 rows = two metrics

    for row, metric_name in enumerate(["modularity", "modularity_motion"]):
        metric_versions = {}
        for v in fmriprep_versions:
            d_v, measure = motion_metrics.load_data(
                path_root, datasets, criteria_name, v, metric_name
            )
            metric_versions[v] = d_v[fixed_dataset][
                ~d_v[fixed_dataset]["strategy"].isin(excluded_strategies)
            ]
        axs = subfigs_mod[row].subplots(1, 2, sharey=True)  # 1 × 2 = versions
        for col, (v, df) in enumerate(metric_versions.items()):
            baseline_mean = df.query("strategy=='baseline'")[measure["label"]].mean()
            sns.barplot(
                x="strategy",
                y=measure["label"],
                data=df.query("groups=='full_sample'"),
                order=strategy_order,
                palette=paired_palette,
                ci=95,
                ax=axs[col],
            )
            axs[col].axhline(baseline_mean, ls="-.", c=paired_palette[0])
            axs[col].set_title(v)
            axs[col].set_ylim(measure["ylim"])
            axs[col].set_xticklabels(strategy_order, rotation=45, ha="right")

        if row == 0:
            labels = ["No GSR", "With GSR"]
            hatches = ["", "///"]
            handles = [
                mpatches.Patch(edgecolor="black", facecolor="white", hatch=h, label=l)
                for h, l in zip(hatches, labels)
            ]
            axs[1].legend(handles=handles)

    fig_mod.savefig(output_dir / "modularity_versions.png", transparent=True)

   # ---------------------------------------------------------------
    # 3e. STRATEGY RANKING  +  prepare table for the scatter plot
    # ---------------------------------------------------------------
    rank_versions = strategy_ranking.load_data(path_root, datasets)

    # keep only the ranking columns and add the expected column-level names
    rank_versions = rank_versions[[c for c in rank_versions.columns
                                if c[0] == "ranking"]]
    rank_versions.columns = pd.MultiIndex.from_tuples(
        rank_versions.columns, names=["measure", "strategy"]
    )

    # 🔑  1.  MAKE A COPY **BEFORE** YOU TOUCH THE INDEX ORDER
    scatter_table = rank_versions.copy()
    scatter_table.index = scatter_table.index.set_names(
        ["dataset", "version", "metrics"]
    )

    # 🔄  2.  NOW swap levels for the heat-map
    rank_versions = rank_versions.swaplevel("dataset", "version")
    rank_versions.index = rank_versions.index.set_names(
        ["dataset", "version", "metrics"]
    )

    # tell the helper to plot two versions across, one dataset down
    strategy_ranking.datasets          = fmriprep_versions   # columns
    strategy_ranking.fmriprep_versions = datasets            # rows

    fig_ranking = strategy_ranking.plot_ranking(rank_versions)
    fig_ranking.savefig(output_dir / "strategy_ranking_versions.png",
                        transparent=True)
    
    # --- 3f.  LOSS-vs-QUALITY SCATTERS -----------------------------
    for v in fmriprep_versions:                # two versions → two PNGs
        plot_loss_vs_quality(
            data=scatter_table,                # has a 'version' level
            output_dir=output_dir,
            version_filter=v
        )
    # ---------------------------------------------------------------
