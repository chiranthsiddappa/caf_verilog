from . caf_verilog_base import CafVerilogBase
from . caf_slice import CAFSlice


class CAFStream(CafVerilogBase):

    def __init__(self, reference, received, freq_res,
                 ref_i_bits=12, ref_q_bits=0,
                 rec_i_bits=12, rec_q_bits=0,
                 fs=625e3, n_bits=8,
                 output_dir='.'):
        self.reference = reference
        self.received = received
        self.fs = fs
        self.n_bits = n_bits
        self.ref_i_bits = ref_i_bits
        self.ref_q_bits = ref_q_bits if ref_q_bits else ref_i_bits
        self.rec_i_bits = rec_i_bits
        self.rec_q_bits = rec_q_bits if rec_q_bits else rec_i_bits
        self.output_dir = output_dir
        self.submodules = self.gen_submodules()
        self.write_module()

    def gen_submodules(self) -> dict:
        submodules = dict()
        submodules['caf_slice'] = CAFSlice(reference=self.reference,
                                           received=self.received,
                                           ref_i_bits=self.ref_i_bits,
                                           ref_q_bits=self.ref_q_bits,
                                           rec_i_bits=self.rec_i_bits,
                                           rec_q_bits=self.rec_q_bits,
                                           fs=self.fs,
                                           n_bits=self.n_bits,
                                           output_dir=self.output_dir)
        return submodules
