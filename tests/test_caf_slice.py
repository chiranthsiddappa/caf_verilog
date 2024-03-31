from unittest import TestCase
from caf_verilog import caf_slice

from tempfile import TemporaryDirectory
import os
import numpy as np

from caf_verilog.sim_helper import sim_shift
from gps_helper.prn import PRN
from caf_verilog.quantizer import quantize
from caf_verilog.xcorr import gen_tb_values
from sk_dsp_comm import sigsys as ss


class TestCAFSlice(TestCase):

    def setUp(self):
        self.center = 300
        self.corr_length = 250
        self.time_shift = 0
        self.freq_shift = 20e3
        self.fs = 625e3
        self.n_quantize_bits = 12
        prn = PRN(10)
        Ns = self.fs / 125e3
        prn_seq = prn.prn_seq()
        prn_seq, b = ss.nrz_bits2(np.array(prn_seq), Ns)
        prn_seq = [*prn_seq, *prn_seq]
        prn_seq = np.array(prn_seq)
        prn_seq = prn_seq + prn_seq * 1j
        ref, rec = sim_shift(prn_seq, self.center, self.corr_length,
                             shift=self.time_shift, freq_shift=self.freq_shift, fs=self.fs)
        self.ref_quant = quantize(ref, n_bits=self.n_quantize_bits)
        self.rec_quant = quantize(rec, n_bits=self.n_quantize_bits)

    def test_verify_via_dot_xcorr(self):
        caf_slice_computed = caf_slice.caf_slice_dot(self.ref_quant, self.rec_quant, self.freq_shift, self.fs)
        index_to_verify = np.argmax(np.abs(caf_slice_computed))
        index_expected = (self.corr_length / 2) - self.time_shift
        assert index_to_verify == index_expected

    def test_caf_slice_output_files(self):
        test_files = ['caf_slice.v', 'cpx_multiply.v', 'dot_prod_pip.v',
                      'freq_shift_625_12_8.v', 'sig_gen_625_12_8.v', 'x_corr.v']
        x = [ii for ii in range(0, 10)]
        y = [ii for ii in range(0, 20)]
        fs = 625e3
        freq_res = 200
        n_bits = 8
        with TemporaryDirectory() as tmpdir:
            caf_slice_inst = caf_slice.CAFSlice(x, y, freq_res=freq_res, fs=fs, n_bits=n_bits, output_dir=tmpdir)
            files = os.listdir(tmpdir)
            for file in test_files:
                self.assertIn(file, files)
