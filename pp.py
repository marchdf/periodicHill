# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import numpy as np
import pandas as pd
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
    parser.add_argument(
        "-m", "--mfile", help="Root name of files to postprocess", required=True
    )
    args = parser.parse_args()

    fdir = os.path.dirname(args.mfile)
    auto_decomp = False

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    par = stk.Parallel.initialize()
    printer = p0_printer(par)

    mesh = stk.StkMesh(par)
    printer("Reading meta data for mesh: ", args.mfile)
    mesh.read_mesh_meta_data(args.mfile, auto_decomp=auto_decomp)
    printer("Done reading meta data")

    printer("Loading bulk data for mesh: ", args.mfile)
    mesh.populate_bulk_data()
    printer("Done reading bulk data")

    num_time_steps = mesh.stkio.num_time_steps
    max_time = mesh.stkio.max_time
    tsteps = mesh.stkio.time_steps
    printer(f"""Num. time steps = {num_time_steps}\nMax. time step  = {max_time}""")
    ftime, missing = mesh.stkio.read_defined_input_fields(tsteps[-1])
    printer(f"Loaded fields for time: {ftime}")

    coords = mesh.meta.coordinate_field

    # Extract spanwise average tau_wall on wall
    wall = mesh.meta.get_part("wall")
    sel = wall & mesh.meta.locally_owned_part

    tauw = mesh.meta.get_field("tau_wall")
    names = ["x", "y", "z", "tauw"]
    nnodes = 0
    for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK):
        nnodes += bkt.size

    cnt = 0
    data = np.zeros((nnodes, 4))
    for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK):
        xyz = coords.bkt_view(bkt)
        tw = tauw.bkt_view(bkt)
        for i in range(bkt.size):
            data[cnt, :] = [xyz[i, 0], xyz[i, 1], xyz[i, 2], tw[i]]
            cnt += 1

    # Gather to root
    lst = comm.gather(data, root=0)
    comm.Barrier()
    if rank == 0:
        df = pd.DataFrame(np.vstack(lst), columns=names)
        tw = df.groupby("x", as_index=False).mean().sort_values(by=["x"])
        twname = os.path.join(fdir, "tw.dat")
        tw.to_csv(twname, index=False)
