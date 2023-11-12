from unittest import TestCase
import numpy.testing as npt
import numpy as np
from caf_verilog import quantizer


class TestQuantizer(TestCase):

    def setUp(self):
        n = np.arange(0, 12)
        self.x = np.cos(2 * np.pi * 0.211 * n)
        self.test_q = np.array([127., 31., -112., -85., 71., 120., -13., -126., -48., 102., 98., -55.])

    def test_x(self):
        test_x = np.array([1., 0.24259923, -0.88229123, -0.67068558, 0.55687562, 0.94088077, -0.10036171, -0.98957612,
                           -0.3797791, 0.80530789, 0.77051324, -0.43145605])
        npt.assert_almost_equal(self.x, test_x)

    def test_quantizer_8_bits(self):
        q = quantizer.quantize(self.x, 8)
        npt.assert_almost_equal(q, self.test_q)

    def test_quantizer_max(self):
        x = self.x * 0.95
        test_q = np.array([121., 29., -107., -81., 67., 114., -12., -120., -46., 97., 93., -52.])
        q = quantizer.quantize(x, 8)
        npt.assert_almost_equal(q, test_q)

    def test_quantizer_cpx_default(self):
        x = self.x
        xj = x * 1j
        x = x + xj
        q = quantizer.quantize(x, 8)
        npt.assert_almost_equal(q.imag, self.test_q)

    def test_quantizer_cpx_8(self):
        x = self.x
        xj = x * 1j
        x = x + xj
        q = quantizer.quantize(x, 3, 8)
        npt.assert_almost_equal(q.imag, self.test_q)
