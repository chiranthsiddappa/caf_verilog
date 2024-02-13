from unittest import TestCase
from caf_verilog import caf_slice
from tempfile import TemporaryDirectory
import os
from numpy import arange


class TestCAFSlice(TestCase):

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
