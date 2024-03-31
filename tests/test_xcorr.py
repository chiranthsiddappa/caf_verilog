from .test_base import TestCafVerilogBase
from gps_helper.prn import PRN
from sk_dsp_comm import sigsys as ss
from numpy import array
from caf_verilog.sim_helper import sim_shift
from caf_verilog import xcorr as xc
from tempfile import TemporaryDirectory
import os


class TestXCorr(TestCafVerilogBase):

    def setUp(self):
        prn = PRN(10)
        prn_seq = prn.prn_seq()
        prn_seq, b = ss.nrz_bits2(array(prn_seq), 5)
        self.prn_seq = prn_seq

    def test_dot_xcorr(self):
        center = 300
        corr_length = 200
        ref, rec = sim_shift(self.prn_seq, center, corr_length, shift=10)
        rr = xc.dot_xcorr(ref, rec)
        self.assertAlmostEqual(max(rr), 200)
        self.assertAlmostEqual(rr[100 - 10], 200)

    def test_x_corr_tb(self):
        center = 300
        corr_length = 200
        ref, rec = sim_shift(self.prn_seq, center, corr_length, shift=10)
        with TemporaryDirectory() as tmpdir:
            xcorr = xc.XCorr(ref, rec, output_dir=tmpdir)
            xcorr.gen_tb()
            files = os.listdir(tmpdir)
            test_files = ['x_corr_tb.v', 'x_corr.v', 'arg_max.v', 'dot_prod_pip.v', 'cpx_multiply.v']
            for file in test_files:
                self.assertIn(file, test_files)

    def test_tb_values(self):
        center = 300
        corr_length = 200
        ref, rec = sim_shift(self.prn_seq, center, corr_length, shift=10)
        ref_tb, rec_tb = xc.gen_tb_values(ref, rec)
        zipped_tb_vals = zip(ref_tb, rec_tb)
        zipped_tb_vals = list(zipped_tb_vals)
        assert len(zipped_tb_vals) == corr_length**2 + corr_length
