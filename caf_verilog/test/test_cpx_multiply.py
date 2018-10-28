from unittest import TestCase
import numpy.testing as npt
import numpy as np
from ..cpx_multiply import CpxMultiply
import os
from tempfile import mkdtemp

class TestCpxMultiply(TestCase):

    def setUp(self):
        n = np.arange(0, 12)
        self.x = np.cos(2 * np.pi * 0.211 * n)
        self.test_x = np.array([127., 31., -113., -86., 71., 120., -13., -127., -49., 103.])

    def test_cpx_multiply_x_real(self):
        cpx_multiply = CpxMultiply(self.x, self.x, x_i_bits=8)
        npt.assert_almost_equal(cpx_multiply.x_quant[:10], self.test_x)

    def test_cpx_multiply_x_imag(self):
        xj = self.x * 1j
        x = self.x + xj
        cpx_multiply = CpxMultiply(x, x, x_q_bits=8)
        npt.assert_almost_equal(cpx_multiply.x_quant.imag[:10], self.test_x)

    def test_cpx_multiply_y_real(self):
        cpx_multiply = CpxMultiply(self.x, self.x, y_i_bits=8)
        npt.assert_almost_equal(cpx_multiply.y_quant[:10], self.test_x)

    def test_cpx_multiply_y_imag(self):
        xj = self.x * 1j
        x = self.x + xj
        cpx_multiply = CpxMultiply(x, x, y_q_bits=8)
        npt.assert_almost_equal(cpx_multiply.y_quant.imag[:10], self.test_x)

    def test_cpx_multiply_gen_tb(self):
        """
        Only tests that the files are written out.
        :return:
        """
        tmpdir = mkdtemp()
        cpx_multiply = CpxMultiply(self.x, self.x, output_dir=tmpdir)
        cpx_multiply.gen_tb()
        files = os.listdir(tmpdir)
        test_files = ['cpx_multiply_tb.v', 'cpx_multiply_input_values.txt', 'cpx_multiply.v']
        for file in test_files:
            self.assertIn(file, files)
