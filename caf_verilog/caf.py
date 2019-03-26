import numpy as np
from sk_dsp_comm import digitalcom as dc
from . caf_verilog_base import CafVerilogBase


class CAF(CafVerilogBase):

    def __init__(self, reference, received, foa, i_bits, q_bits, output_dir='.'):
        """

        :param reference:
        :param received:
        :param i_bits:
        :param q_bits:
        :param output_dir:
        """
        self.reference = reference
        self.received = received
        self.foa = foa
        self.i_bits = i_bits
        self.q_bits = q_bits
        self.output_dir = output_dir
