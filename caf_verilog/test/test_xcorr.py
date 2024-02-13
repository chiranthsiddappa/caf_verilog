from .test_base import TestCafVerilogBase
from gps_helper.prn import PRN
from sk_dsp_comm import sigsys as ss
from numpy import array
from ..sim_helper import sim_shift
from .. import xcorr as xc
from tempfile import mkdtemp
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
        self.assertAlmostEquals(rr[100 - 10], 200)

    def test_x_corr_tb(self):
        tmpdir = mkdtemp()
        center = 300
        corr_length = 200
        ref, rec = sim_shift(self.prn_seq, center, corr_length, shift=10)
        xcorr = xc.XCorr(ref, rec, output_dir=tmpdir)
        xcorr.gen_tb()
        files = os.listdir(tmpdir)
        test_files = ['x_corr_tb.v', 'x_corr.v', 'arg_max.v', 'dot_prod_pip.v', 'cpx_multiply.v']
        for file in test_files:
            self.assertIn(file, test_files)
