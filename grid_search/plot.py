import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


def figure_size(width, fraction=1):
    fig_width_pt = width * fraction
    inches_per_pt = 1 / 72.27
    golden_ratio = (5**.5 - 1) / 2
    fig_width_in = fig_width_pt * inches_per_pt
    fig_height_in = fig_width_in * golden_ratio

    return (fig_width_in, fig_height_in)


def set_plt_rc():
    # To make times new roman have normal boldness
    # See https://stackoverflow.com/a/44386835/7280039
    del matplotlib.font_manager.weight_dict['roman']
    matplotlib.font_manager._rebuild()

    font = {
        "family": "Times New Roman",
        "size": 12,
    }
    plt.rc("font", **font)

    # > 469.47049pt.
    # l.15 \showthe\textwidth
    figure = {
        "figsize": figure_size(469.47049)
    }
    plt.rc("figure", **figure)

    axes = {
        "grid": True
    }
    plt.rc("axes", **axes)


def parse_args():
    ap = argparse.ArgumentParser(description="Reads grid search results csv and plots results.")
    ap.add_argument("--cv-results", type=str, required=True, help="File with cv results")
    ap.add_argument("--change", type=str, required=True, help="Changing parameter")
    ap.add_argument("--param", type=str, default=None, help="Additional parameter")
    ap.add_argument("--precision-file", type=str, default="./precision.pdf", help="File to output precision plot")
    ap.add_argument("--recall-file", type=str, default="./recall.pdf", help="File to output recall plot")
    return ap.parse_args()


def plot_group(group, change, ax, metric, label=None):
    X = group[f"param_{change}"]
    y = group[f"mean_test_{metric}"]
    ax.plot(X, y, label=label)
    ax.set_xlabel(change)
    ax.set_ylabel(metric)


def plot_single_param(cv_results, change, outputs, metrics=["precision", "recall"]):
    for metric, output in zip(metrics, outputs):
        fig = plt.figure()
        ax = fig.gca()
        plot_group(cv_results, change, ax, metric)
        fig.savefig(output, bbox_inches='tight')


def plot_double_param(cv_results, change, outputs, param, metrics=["precision", "recall"]):
    for metric, output in zip(metrics, outputs):
        fig = plt.figure()
        ax = fig.gca()
        for index, group in cv_results.groupby(f"param_{param}"):
            plot_group(group, change, ax, metric, f"{param} = {index}")

        ax.legend(loc="best")
        fig.savefig(output, bbox_inches='tight')


if __name__ == "__main__":
    args = parse_args()
    set_plt_rc()
    cv_results = pd.read_csv(args.cv_results)
    outputs = [args.precision_file, args.recall_file]
    if args.param is None:
        plot_single_param(cv_results, args.change, outputs)
    else:
        plot_double_param(cv_results, args.change, outputs, args.param)

    for metric in ["precision", "recall"]:
        idxmax = cv_results[f"mean_test_{metric}"].idxmax()
        best_params, metric_max = cv_results["params"][idxmax], cv_results[f"mean_test_{metric}"][idxmax]
        print(f"{metric} reaches maximum of {metric_max} at {best_params}")