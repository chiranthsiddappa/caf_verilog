import numpy as np
from sk_dsp_comm import digitalcom as dc
from . caf_verilog_base import CafVerilogBase


class CAF(CafVerilogBase):

    def __init__(self, reference, received, foa, i_bits, q_bits, output_dir='.'):
        """

        :param reference:
        :param received:
        :param i_bits:
        :param q_bits:
        :param output_dir:
        """
        self.reference = reference
        self.received = received
        self.foa = foa
        self.i_bits = i_bits
        self.q_bits = q_bits
        self.output_dir = output_dir


def simple_caf(x, y, foas, fs):
    """
    Produce values for a surface plot of the Complex Ambiguity Function.
    This function primarily supports testing values produced via sim_helper, so y is expected to be twice the length of
    x.
    The return is the CAF surface and a time delay range normalized by the sampling frequency.

    :param x: Use x as a reference signal.
    :param y: Use y as a captured signal.
    :param foas: Frequency offsets, provided as a list/iterable object.
    :param fs: Sampling frequency
    :return: caf_res, dt
    """
    nlags = len(x)
    ztup = (nlags, len(foas))
    caf_res = np.zeros(ztup)
    nlen = len(y)
    nrange = np.arange(0, nlen)
    dt_lags = nlags // 2
    dt = np.arange(-dt_lags, dt_lags) / float(fs)
    for k, Df in enumerate(foas):
        theta = np.exp(1j*2*np.pi*nrange*Df/float(fs))
        y_shift = y * theta
        rxy, lags = dc.xcorr(x, y_shift, nlags)
        caf_res[:, k] = np.abs(rxy)
    return caf_res, dt
