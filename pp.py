# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import numpy as np
from mpi4py import MPI
import stk


# ========================================================================
#
# Functions
#
# ========================================================================
def p0_printer(par):
    iproc = par.rank

    def printer(*args, **kwargs):
        if iproc == 0:
            print(*args, **kwargs)

    return printer


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="A simple post-processing tool")
    parser.add_argument("-f", "--fdir", help="Files to postprocess", required=True)
    args = parser.parse_args()
