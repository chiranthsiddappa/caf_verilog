from unittest import TestCase
from .. import sig_gen as sg
from tempfile import mkdtemp
import os


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

    def test_sig_gen_gen_tb(self):
        tmpdir = mkdtemp()
        sig_gen = sg.SigGen(1200, 625e3, 8, output_dir=tmpdir)
        sig_gen.gen_tb()
        files = os.listdir(tmpdir)
        test_files = ['sig_gen_tb.v', 'sig_gen_625_10_8.txt', 'sig_gen_625_10_8.v']
        for file in test_files:
            self.assertIn(file, files)

