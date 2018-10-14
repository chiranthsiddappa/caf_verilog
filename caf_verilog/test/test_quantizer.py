from unittest import TestCase
import numpy.testing as npt
import numpy as np
from .. import quantizer


class TestQuantizer(TestCase):

    def test_quantizer_8_bits(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        test_q = np.array([254., 62., -226., -172., 142., 240., -26., -254., -98., 206.])
        q = quantizer.quantize(x, 8)
        npt.assert_almost_equal(q[:10], test_q)

    def test_quantizer_max(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n) * 0.95
        test_q = np.array([244., 60., -214., -164., 136., 228., -24., -240., -92., 196.])
        q = quantizer.quantize(x, 8)
        npt.assert_almost_equal(q[:10], test_q)

    def test_quantizer_cpx_default(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        xj = x * 1j
        x = x + xj
        test_q = np.array([254., 62., -226., -172., 142., 240., -26., -254., -98., 206.])
        q = quantizer.quantize(x, 8)
        npt.assert_almost_equal(q.imag[:10], test_q)

    def test_quantizer_cpx_8(self):
        n = np.arange(0, 12)
        x = np.cos(2 * np.pi * 0.211 * n)
        xj = x * 1j
        x = x + xj
        test_q = np.array([254., 62., -226., -172., 142., 240., -26., -254., -98., 206.])
        q = quantizer.quantize(x, 3, 8)
        npt.assert_almost_equal(q.imag[:10], test_q)
