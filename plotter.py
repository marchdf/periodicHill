#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import glob
import yaml
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import pandas as pd
import utilities

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
    mapping = {f"{k+1:03d}": x for k, x in enumerate(utilities.xplanes())}
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
def parse_ic(fname):
    """Parse the Nalu yaml input file for the initial conditions"""
    with open(fname, "r") as stream:
        try:
            dat = yaml.load(stream)
            u0 = float(
                dat["realms"][0]["initial_conditions"][0]["value"]["velocity"][0]
            )
            rho0 = float(
                dat["realms"][0]["material_properties"]["specifications"][0]["value"]
            )
            mu = float(
                dat["realms"][0]["material_properties"]["specifications"][1]["value"]
            )

            return u0, rho0, mu

        except yaml.YAMLError as exc:
            print(exc)


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

        idx = group.y.values >= utilities.hill(group.x.values)
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

        idx = group.y.values >= utilities.hill(group.x.values)
        plt.figure("u")
        p = plt.plot(group[idx].u + group[idx].x, group[idx].y, lw=2, color=cmap[0])

        plt.figure("v")
        p = plt.plot(group[idx].v + group[idx].x, group[idx].y, lw=2, color=cmap[0])

    cf = pd.read_csv(
        os.path.join(ldir, "hill_LES_cf_digitized.dat"), delim_whitespace=True
    )
    plt.figure("cf")
    plt.plot(cf.x, cf.cf, lw=2, color=cmap[0], label="LES")

    # Nalu data
    yname = os.path.join(os.path.dirname(args.fdir), "periodicHill.yaml")
    u0, rho0, mu = parse_ic(yname)
    dynPres = rho0 * 0.5 * u0 * u0
    ndf = pd.read_csv(os.path.join(args.fdir, "profiles.dat"))
    grouped = ndf.groupby(["x"])
    for k, (name, group) in enumerate(grouped):

        idx = group.y.values >= utilities.hill(group.x.values)
        plt.figure("u")
        p = plt.plot(group[idx].u + group[idx].x, group[idx].y, lw=2, color=cmap[1])

        plt.figure("v")
        p = plt.plot(group[idx].v + group[idx].x, group[idx].y, lw=2, color=cmap[1])

    cf = pd.read_csv(os.path.join(args.fdir, "tw.dat"))
    cf["cf"] = cf.tauw
    plt.figure("cf")
    plt.plot(cf.x, cf.cf, lw=2, color=cmap[1], label="Nalu")

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
        Line2D([0], [0], lw=2, color=cmap[1], label="Nalu"),
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
