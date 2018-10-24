from unittest import TestCase
import numpy.testing as npt
import numpy as np
from ..cpx_multiply import CpxMultiply


class TestCpxMultiply(TestCase):

    def test_cpx_multiply_x_real(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        cpx_multiply = CpxMultiply(x, x, x_i_bits=8)
        test_x = np.array([255., 62., -226., -172., 143., 241., -26., -253., -97., 206.])
        npt.assert_almost_equal(cpx_multiply.x_quant[:10], test_x)

    def test_cpx_multiply_x_imag(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        xj = x * 1j
        x = x + xj
        test_x_i = np.array([255., 62., -226., -172., 143., 241., -26., -253., -97., 206.])
        cpx_multiply = CpxMultiply(x, x, x_q_bits=8)
        npt.assert_almost_equal(cpx_multiply.x_quant.imag[:10], test_x_i)

    def test_cpx_multiply_y_real(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        cpx_multiply = CpxMultiply(x, x, y_i_bits=8)
        test_y = np.array([255., 62., -226., -172., 143., 241., -26., -253., -97., 206.])
        npt.assert_almost_equal(cpx_multiply.y_quant[:10], test_y)

    def test_cpx_multiply_y_imag(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        xj = x * 1j
        x = x + xj
        test_y_i = np.array([255., 62., -226., -172., 143., 241., -26., -253., -97., 206.])
        cpx_multiply = CpxMultiply(x, x, x_q_bits=8)
        npt.assert_almost_equal(cpx_multiply.x_quant.imag[:10], test_y_i)
