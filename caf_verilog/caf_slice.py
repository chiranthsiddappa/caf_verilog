from .caf_verilog_base import CafVerilogBase
from .xcorr import XCorr, send_and_receive, gen_tb_values
from .freq_shift import FreqShift

import numpy as np
from .dot_product import dot_product


class CAFSlice(CafVerilogBase):

    def __init__(self, reference, received, freq_res,
                 ref_i_bits=12, ref_q_bits=0,
                 rec_i_bits=12, rec_q_bits=0,
                 fs=625e3, n_bits=8,
                 output_dir='.'):
        """

        """
        self.reference = reference
        self.received = received
        self.freq_res = freq_res
        self.fs = fs
        self.n_bits = n_bits
        self.ref_i_bits = ref_i_bits
        self.ref_q_bits = ref_q_bits if ref_q_bits else ref_i_bits
        self.rec_i_bits = rec_i_bits
        self.rec_q_bits = rec_q_bits if rec_q_bits else rec_q_bits
        self.output_dir = output_dir
        self.submodules = self.gen_submodules()
        self.write_module()

    def gen_submodules(self) -> dict:
        submodules = dict()
        submodules['freq_shift'] = FreqShift(self.received, self.freq_res, self.fs, self.n_bits,
                                             i_bits=self.rec_i_bits, q_bits=self.rec_q_bits,
                                             output_dir=self.output_dir)
        submodules['x_corr'] = XCorr(self.reference, self.received, self.ref_i_bits, self.ref_q_bits,
                                     self.rec_i_bits, self.rec_q_bits, pipeline=True, output_dir=self.output_dir)
        return submodules

    def params_dict(self) -> dict:
        pd = {**self.submodules['x_corr'].params_dict(), **self.submodules['freq_shift'].params_dict()}
        return pd

    def template_dict(self, inst_name=None) -> dict:
        t_dict = {**self.submodules['x_corr'].template_dict(), **self.submodules['freq_shift'].template_dict()}
        return t_dict


def caf_slice_dot(ref, rec, f_shift, fs) -> list:
    """
    Perform the cross correlation using the dot product. Shift the reference signal to match the received signal.
    This produces an output list of magnitudes that are inverse offset from the center
    of the reference signal.

    :param ref: Reference signal
    :param rec: Received signal
    :param f_shift: Frequency Shift expected
    :param fs: Sample frequency
    """
    t = np.arange(0, len(rec))
    slice_shift = np.exp(2 * np.pi * (-f_shift / fs) * t * 1j)
    dx = []
    ref_len = len(ref)
    for i in range(0, len(rec) - ref_len + 1):
        ref_nth_shift = ref * slice_shift[i:ref_len + i]
        dx.append(dot_product(ref_nth_shift, rec[i:ref_len + i]))
    return dx
