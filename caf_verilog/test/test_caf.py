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
