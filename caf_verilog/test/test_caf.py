from unittest import TestCase
from .. import caf
from tempfile import mkdtemp
import os
from numpy import arange


class TestCAF(TestCase):

    def test_caf_tb_length(self):
        """
        Test that the files are all written out.
        :return:
        """
        tmpdir = mkdtemp()
        x = [ii for ii in range(0, 10)]
        y = [ii for ii in range(0, 10)]
        foas = arange(-10, 10) * 0.25
        with self.assertRaisesRegex(ValueError, 'Received signal must be twice the length of the reference signal'):
            caf_inst = caf.CAF(x, y, foas, output_dir=tmpdir)

    def test_caf_output_files(self):
        test_files = ['caf.v', 'caf_tb.v']
        tmpdir = mkdtemp()
        x = [ii for ii in range(0, 10)]
        y = [ii for ii in range(0, 20)]
        foas = arange(-10, 10) * 0.25
        caf_inst = caf.CAF(x, y, foas, output_dir=tmpdir)
        files = os.listdir(tmpdir)
        test_files = ['arg_max.v', 'caf.v', 'caf_state_params.v', 'cpx_multiply.v', 'dot_prod_pip.v',
                      'freq_shift_625_23_8.v', 'sig_gen_625_23_8.v', 'x_corr.v']
        for file in test_files:
            self.assertIn(file, files)
