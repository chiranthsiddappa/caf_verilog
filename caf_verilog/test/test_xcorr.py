from .test_base import TestCafVerilogBase
from gps_helper.prn import PRN
from sk_dsp_comm import sigsys as ss
from numpy import array
from ..sim_helper import sim_shift
from .. import xcorr as xc


class TestXCorr(TestCafVerilogBase):

    def setUp(self):
        prn = PRN(10)
        prn_seq = prn.prn_seq()
        prn_seq, b = ss.NRZ_bits2(array(prn_seq), 5)
        self.prn_seq = prn_seq

    def test_dot_xcorr(self):
        center = 300
        corr_length = 200
        ref, rec = sim_shift(self.prn_seq, center, corr_length, shift=10)
        rr = xc.dot_xcorr(ref, rec)
        self.assertAlmostEqual(max(rr), 200)
        self.assertAlmostEquals(rr[100 - 10], 200)