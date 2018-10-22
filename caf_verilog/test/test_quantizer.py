from unittest import TestCase
import numpy.testing as npt
import numpy as np
from .. import quantizer


class TestQuantizer(TestCase):

    def test_quantizer_8_bits(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        test_q = np.array([255., 62., -226., -172., 143., 241., -26., -253., -97., 206.])
        q = quantizer.quantize(x, 8)
        npt.assert_almost_equal(q[:10], test_q)

    def test_quantizer_max(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n) * 0.95
        test_q = np.array([243., 59., -215., -163., 135., 229., -24., -241., -92., 196.])
        q = quantizer.quantize(x, 8)
        npt.assert_almost_equal(q[:10], test_q)

    def test_quantizer_cpx_default(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        xj = x * 1j
        x = x + xj
        test_q = np.array([255., 62., -226., -172., 143., 241., -26., -253., -97., 206.])
        q = quantizer.quantize(x, 8)
        npt.assert_almost_equal(q.imag[:10], test_q)

    def test_quantizer_cpx_8(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        xj = x * 1j
        x = x + xj
        test_q = np.array([255., 62., -226., -172., 143., 241., -26., -253., -97., 206.])
        q = quantizer.quantize(x, 3, 8)
        npt.assert_almost_equal(q.imag[:10], test_q)
