from logging import getLogger
import numpy as np

try:
    from cocotb.runner import get_runner, Simulator
except ImportError as ie:
    import warnings
    Simulator = object
    warnings.warn("Could not import cocotb", ImportWarning)
import os

__hdl_toplevel_lang__ = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
__sim__ = os.getenv("SIM", "verilator")


def sim_get_runner() -> Simulator:
    return get_runner(__sim__)


def get_sim_cpus() -> int:
    num_cpus = len(os.sched_getaffinity(0))
    num_cpus = max(int(num_cpus / 2), 1)
    return num_cpus


def sim_shift(ref, ref_center, ref_length, shift=0, rec=None, padding=False,
              freq_shift=0, fs=625e3):
    """

    :param ref: Reference signal.
    :param ref_center: Where to center the simulated signal set.
    :param ref_length: The length of the signal equidistant around center.
    :param shift: How much shift should be added to the simulated received signal.
    :param rec: A received signal can be provided for the correlation simulation.
    :param padding: Use padding to add zeros on the reference signal; ex. for generating a plot.
    :param freq_shift: Apply a frequency shift to the reference signal, and return with shift as received.
    :param fs: Sampling Frequency
    :return: ref, rec
    :rtype: tuple
    """
    sim_center = ref_center + shift
    fill_length = int(ref_length / 2)
    index_error = not ((ref_center - ref_length) > 0)
    index_error |= not ((ref_center + ref_length) < len(ref))
    if index_error:
        raise IndexError("Center and length result in an out of bounds error in ref")
    if rec:
        index_error |= not ((ref_center + ref_length) < len(rec))
        if index_error:
            raise IndexError("Center and length result in an out of bounds error in rec")
    t = np.arange(len(ref))
    x_shift = np.exp(2 * np.pi * (freq_shift / fs) * t * 1j)
    ref_plus_shift = [ref[i] * x_i_shift for i, x_i_shift in enumerate(x_shift)]
    ref_ret = ref[ref_center - fill_length: ref_center + fill_length]
    if padding:
        fill_zeros = [0 for zz in range(0, fill_length)]
        ref_ret = fill_zeros + list(ref_ret)
        ref_ret += fill_zeros
    if rec:
        rec_ret = rec[sim_center - ref_length:sim_center + ref_length]
    else:
        rec_ret = ref_plus_shift[sim_center - ref_length: sim_center + ref_length]
    return ref_ret, rec_ret

