#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import pandas as pd


# ========================================================================
#
# Some defaults variables
#
# ========================================================================
plt.rc("text", usetex=True)
cmap_med = [
    "#F15A60",
    "#7AC36A",
    "#5A9BD4",
    "#FAA75B",
    "#9E67AB",
    "#CE7058",
    "#D77FB4",
    "#737373",
]
cmap = [
    "#EE2E2F",
    "#008C48",
    "#185AA9",
    "#F47D23",
    "#662C91",
    "#A21D21",
    "#B43894",
    "#010202",
]
dashseq = [
    (None, None),
    [10, 5],
    [10, 4, 3, 4],
    [3, 3],
    [10, 4, 3, 4, 3, 4],
    [3, 3],
    [3, 3],
]
markertype = ["s", "d", "o", "p", "h"]


# ========================================================================
#
# Functions
#
# ========================================================================
def read_exp_data(fdir):
    lst = []
    for fname in glob.glob(fdir + "/*.dat"):
        with open(fname, "r") as f:
            for line in f:
                if line.startswith("# x/h"):
                    x = float(line.split("=")[-1])
                    break

        df = pd.read_csv(
            fname,
            header=None,
            names=["y", "u", "v", "upup", "vpvp", "upvp"],
            comment="#",
        )
        df["x"] = x
        lst.append(df)

    return pd.concat(lst, ignore_index=True)


# ========================================================================
def read_les_data(fdir):
    lst = []
    pfx = "UFR3-30_C_10595_data_MB-"
    mapping = {
        "001": 0.05,
        "002": 0.5,
        "003": 1.0,
        "004": 2.0,
        "005": 3.0,
        "006": 4.0,
        "007": 5.0,
        "008": 6.0,
        "009": 7.0,
        "010": 8.0,
    }
    for k, v in mapping.items():
        fname = os.path.join(fdir, pfx + k + ".dat")

        df = pd.read_csv(
            fname,
            header=None,
            names=["y", "u", "v", "upup", "vpvp", "upvp", "k"],
            delim_whitespace=True,
            comment="#",
        )
        df["x"] = v
        lst.append(df)

    return pd.concat(lst, ignore_index=True)


# ========================================================================
def hill(x):
    h = 28.0
    xstar = x * h
    xstar[xstar > 128] = 252 - xstar[xstar > 128]
    ystar = np.zeros(x.shape)
    idx = (0.0 <= xstar) & (xstar < 9.0)
    ystar[idx] = np.minimum(
        28 * np.ones(x[idx].shape),
        2.800000000000e01
        + 0.000000000000e00 * xstar[idx]
        + 6.775070969851e-03 * xstar[idx] ** 2
        - 2.124527775800e-03 * xstar[idx] ** 3,
    )
    idx = (9.0 <= xstar) & (xstar < 14.0)
    ystar[idx] = (
        2.507355893131e01
        + 9.754803562315e-01 * xstar[idx]
        - 1.016116352781e-01 * xstar[idx] ** 2
        + 1.889794677828e-03 * xstar[idx] ** 3
    )
    idx = (14.0 <= xstar) & (xstar < 20.0)
    ystar[idx] = (
        2.579601052357e01
        + 8.206693007457e-01 * xstar[idx]
        - 9.055370274339e-02 * xstar[idx] ** 2
        + 1.626510569859e-03 * xstar[idx] ** 3
    )
    idx = (20.0 <= xstar) & (xstar < 30.0)
    ystar[idx] = (
        4.046435022819e01
        - 1.379581654948e00 * xstar[idx]
        + 1.945884504128e-02 * xstar[idx] ** 2
        - 2.070318932190e-04 * xstar[idx] ** 3
    )
    idx = (30.0 <= xstar) & (xstar < 40.0)
    ystar[idx] = (
        1.792461334664e01
        + 8.743920332081e-01 * xstar[idx]
        - 5.567361123058e-02 * xstar[idx] ** 2
        + 6.277731764683e-04 * xstar[idx] ** 3
    )
    idx = (40.0 <= xstar) & (xstar < 50.0)
    ystar[idx] = np.maximum(
        np.zeros(x[idx].shape),
        5.639011190988e01
        - 2.010520359035e00 * xstar[idx]
        + 1.644919857549e-02 * xstar[idx] ** 2
        + 2.674976141766e-05 * xstar[idx] ** 3,
    )

    return ystar / h


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="A simple plot tool")
    parser.add_argument("-f", "--fdir", help="Folder to plot", required=True)
    args = parser.parse_args()

    # Reference data
    refdir = os.path.abspath("refdata")
    edir = os.path.join(refdir, "exp")
    ldir = os.path.join(refdir, "les")
    edf = read_exp_data(edir)
    ldf = read_les_data(ldir)
    figsize = (15, 6)

    grouped = edf.groupby(["x"])
    for k, (name, group) in enumerate(grouped):

        idx = group.y.values >= hill(group.x.values)
        plt.figure("u", figsize=figsize)
        p = plt.plot(
            group[idx].u + group[idx].x,
            group[idx].y,
            lw=0,
            color=cmap[-1],
            marker=markertype[2],
            mec=cmap[-1],
            mfc=cmap[-1],
            ms=3,
        )

        plt.figure("v", figsize=figsize)
        p = plt.plot(
            group[idx].v + group[idx].x,
            group[idx].y,
            lw=0,
            color=cmap[-1],
            marker=markertype[2],
            mec=cmap[-1],
            mfc=cmap[-1],
            ms=3,
        )

    grouped = ldf.groupby(["x"])
    for k, (name, group) in enumerate(grouped):

        idx = group.y.values >= hill(group.x.values)
        plt.figure("u")
        p = plt.plot(group[idx].u + group[idx].x, group[idx].y, lw=2, color=cmap[0])

        plt.figure("v")
        p = plt.plot(group[idx].v + group[idx].x, group[idx].y, lw=2, color=cmap[0])

    cf = pd.read_csv(
        os.path.join(ldir, "hill_LES_cf_digitized.dat"), delim_whitespace=True
    )
    plt.figure("cf")
    plt.plot(cf.x, cf.cf, lw=2, color=cmap[0], label="LES")

    # Save the plots
    fname = "plots.pdf"
    legend_elements = [
        Line2D(
            [0],
            [0],
            lw=0,
            marker=markertype[2],
            color=cmap[-1],
            mfc=cmap[-1],
            mec=cmap[-1],
            markersize=3,
            label="Exp.",
        ),
        Line2D([0], [0], lw=2, color=cmap[0], label="LES"),
    ]

    with PdfPages(fname) as pdf:
        plt.figure("u")
        ax = plt.gca()
        plt.xlabel(r"$\langle u_x \rangle + x$", fontsize=22, fontweight="bold")
        plt.ylabel(r"$y / h$", fontsize=22, fontweight="bold")
        plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
        plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
        plt.xlim([-0.5, 9.5])
        plt.ylim([0, 3.5])
        legend = ax.legend(handles=legend_elements, loc="best")
        plt.tight_layout()
        pdf.savefig(dpi=300)

        plt.figure("v")
        ax = plt.gca()
        plt.xlabel(r"$\langle u_x \rangle + x$", fontsize=22, fontweight="bold")
        plt.ylabel(r"$y / h$", fontsize=22, fontweight="bold")
        plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
        plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
        plt.xlim([-0.5, 9.5])
        plt.ylim([0, 3.5])
        legend = ax.legend(handles=legend_elements, loc="best")
        plt.tight_layout()
        pdf.savefig(dpi=300)

        plt.figure("cf")
        ax = plt.gca()
        plt.xlabel(r"$x$", fontsize=22, fontweight="bold")
        plt.ylabel(r"$c_f$", fontsize=22, fontweight="bold")
        plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
        plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
        legend = ax.legend(loc="best")
        plt.tight_layout()
        pdf.savefig(dpi=300)
