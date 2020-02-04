import numpy as np


# ========================================================================
def p0_printer(par):
    iproc = par.rank

    def printer(*args, **kwargs):
        if iproc == 0:
            print(*args, **kwargs)

    return printer


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
def xplanes():
    return [0.05, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
