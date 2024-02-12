from .caf_verilog_base import CafVerilogBase
from .xcorr import XCorr
from .freq_shift import FreqShift


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
