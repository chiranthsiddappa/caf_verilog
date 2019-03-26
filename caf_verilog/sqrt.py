from . caf_verilog_base import CafVerilogBase


class Sqrt(CafVerilogBase):
    """
    Binary sqrt implementation.
    """

    def __init__(self, n_bits, output_dir='.'):
        self.n_bits = n_bits
        self.output_dir = output_dir


def bin_sqrt(num, bits):
    """
    Compute a sqrt using binary operations only.
    Python implementation of [1]_.
    :param num: Number to take sqrt of
    :param bits: Number of bits to simulate
    :return:


    .. [1] M. Guy, "Square root by abacus algorithm", 1985
    """
    if num > 2 ** bits:
        raise ValueError("num must be less than 2 ** bits")
    res = 0
    bnum = num
    bit = 1 << (bits - 2)

    while bit > bnum:
        bit = bit >> 2
    while bit != 0:
        if bnum >= res + bit:
            bnum = bnum - res + bit
            res = (res >> 1) + bit
        else:
            res = res >> 1
        bit = bit >> 2
    return res
