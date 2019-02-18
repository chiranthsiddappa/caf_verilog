from . caf_verilog_base import CafVerilogBase
from .quantizer import quantize
from numpy import dot as ndot


class XCorr(CafVerilogBase):

    def __init__(self, ref, rec, ref_i_bits=12, ref_q_bits=0,
                 rec_i_bits=12, rec_q_bits=0,
                 pipeline=False):
        """

        :param ref: Reference signal.
        :param rec: Received or simulated secondary signal.
        :param ref_i_bits:
        :param ref_q_bits:
        :param rec_i_bits:
        :param rec_q_bits:
        :param pipeline:
        """
        self.ref = ref
        self.rec = rec
        self.ref_i_bits = ref_i_bits
        self.ref_q_bits = ref_q_bits
        self.rec_i_bits = rec_i_bits
        self.rec_q_bits = rec_q_bits
        self.pip = pipeline
        self.ref_quant = quantize(self.ref, self.ref_i_bits, self.ref_q_bits)
        self.rec_quant = quantize(self.rec, self.rec_i_bits, self.rec_q_bits)

    def gen_quantized_output(self):
        """

        :return:
        """


def dot_xcorr(ref, rec):
    """
    Perform the cross correlation using the dot product.
    This produces an output list of magnitudes that are inverse offset from the center
    of the reference signal.

    :param ref:
    :param rec:
    :return:
    """
    dx = []
    for i in range(0, len(rec) - len(ref)):
        dx.append(ndot(ref, rec[i:len(ref) + i]))
    return dx


def simple_xcorr(f, g, nlags):
    """

    :param f:
    :param g:
    :param nlags:
    :return:
    """
    sums = []
    space = range(-nlags, nlags + 1)
    for n in space:
        sum = 0
        for m in range(0, len(g)):
            cc_index = m + n
            if cc_index >= 0 and cc_index < len(g):
                sum += f[m] * g[cc_index]
        sums.append(sum)
    return sums, space


def size_visualization(f, g, nlags):
    space = range(-nlags, nlags + 1)
    for n in space:
        n_indexes = []
        for m in range(0, len(g)):
            cc_index = m + n
            if cc_index >= 0 and cc_index < len(g):
                n_indexes.append((m, cc_index))
        spacing = " " * int(n >= 0)
        print("n: " + spacing + str(n) + " " + str(n_indexes))