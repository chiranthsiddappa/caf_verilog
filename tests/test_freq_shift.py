from unittest import TestCase
from caf_verilog import freq_shift
from tempfile import TemporaryDirectory
import os
import numpy as np


class TestFreqShift(TestCase):

    def test_freq_shift_gen_tb(self):
        """
        Test that the files are written out
        :return:
        """
        fs = 625e3
        freq_res = 200
        n = np.arange(0, 10000)
        x = np.exp(2 * np.pi * ((50e3) / fs) * n * 1j)
        with TemporaryDirectory() as tmpdir:
            fq = freq_shift.FreqShift(x, freq_res, fs, 8, output_dir=tmpdir)
            fq.gen_tb(20000)
            files = os.listdir(tmpdir)
            test_files = ['freq_shift_tb.v', 'freq_shift_625_12_8.v', 'sig_gen_625_12_8.v', 'sig_gen_625_12_8.txt',
                          'freq_shift_625_12_8_input_values.txt']
            for file in test_files:
                self.assertIn(file, files)
