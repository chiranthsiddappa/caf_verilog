from unittest import TestCase
from caf_verilog import arg_max as am
from tempfile import TemporaryDirectory
import os


class ArgMax(TestCase):

    def test_arg_max_tb(self):
        """
        Test that the files are written out
        :return:
        """
        x = [ii for ii in range(0, 100)]
        with TemporaryDirectory() as tmpdir:
            arg_max = am.ArgMax(x, output_dir=tmpdir)
            arg_max.gen_tb()
            files = os.listdir(tmpdir)
            test_files = ['arg_max_tb.v', 'arg_max.v', 'arg_max_input_values.txt']
            for file in test_files:
                self.assertIn(file, files)
