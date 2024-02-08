from unittest import TestCase
from caf_verilog import caf_slice
from tempfile import TemporaryDirectory
import os
from numpy import arange


class TestCAFSlice(TestCase):

    def test_caf_slice_output_files(self):
        test_files = ['caf_slice.v', 'cpx_multiply.v', 'dot_prod_pip.v',
                      'freq_shift_625_23_8.v', 'sig_gen_625_23_8.v', 'x_corr.v']
        x = [ii for ii in range(0, 10)]
        y = [ii for ii in range(0, 20)]
        foas = arange(-10, 10) * 0.25
        with TemporaryDirectory() as tmpdir:
            caf_slice_inst = caf_slice.CAFSlice(x, y, foas, output_dir=tmpdir)
            files = os.listdir(tmpdir)
            for file in test_files:
                self.assertIn(file, files)
