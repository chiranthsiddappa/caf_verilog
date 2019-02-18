from .test_base import TestCafVerilogBase
from gps_helper.prn import PRN
from sk_dsp_comm import sigsys as ss
from numpy import array


class TestXCorr(TestCafVerilogBase):

    def setUp(self):
        prn = PRN(10)
        prn_seq = prn.prn_seq()
        prn_seq, b = ss.NRZ_bits2(array(prn_seq), 5)
        self.prn_seq = prn_seq