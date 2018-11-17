from unittest import TestCase
from .. import sig_gen as sg


class TestSigGen(TestCase):

    def test_phase_increment(self):
        fclk = 120e6
        nbits = 10
        test_inc = sg.phase_increment(1.40625e6, nbits, fclk)
        inc = 12
        self.assertEqual(inc, test_inc)

    def test_phase_bits(self):
        fclk = 100e6
        precision = 1
        nbits = 27
        test_nbits = sg.phase_bits(fclk, precision)
        self.assertEqual(nbits, test_nbits)

    def test_phase_increment_xil(self):
        fclk = 100e6
        nbits = 18
        test_inc = sg.phase_increment(19e6, nbits, fclk)
        inc = 49807
        self.assertEqual(inc, test_inc)
