from unittest import TestCase
from .. import dot_prod_pip as dpp
from tempfile import mkdtemp
import os


class TestDotProdPip(TestCase):

    def test_dot_prod_pip_tb(self):
        """
        Test that the files are written out.
        :return:
        """
        tmpdir = mkdtemp()
        x = [ii for ii in range(0, 10)]
        y = [ii for ii in range(0, 10)]
        dot_prod_pip = dpp.DotProdPip(x, y, output_dir=tmpdir)
        dot_prod_pip.gen_tb()
        files = os.listdir(tmpdir)
        test_files = ['dot_prod_pip.v', 'dot_prod_pip_tb.v', 'dot_prod_pip_input_values.txt']
        for file in test_files:
            self.assertIn(file, files)