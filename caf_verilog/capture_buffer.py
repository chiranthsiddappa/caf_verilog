from .reference_buffer import ReferenceBuffer
import os
import numpy as np
from . quantizer import quantize

filedir = os.path.dirname(os.path.realpath(__file__))


class CaptureBuffer(ReferenceBuffer):

    def __init__(self, length, i_bits=12, q_bits=12, output_dir='.', name=None):
        self.length = length
        self.i_bits = i_bits
        self.q_bits = q_bits
        self.output_dir = output_dir
        self.tb_filename = '%s_tb.v' % (self.module_name())
        self.buffer = np.random.random(length) + np.random.random(length) * 1j
        self.buffer_quant = quantize(self.buffer, self.i_bits, self.q_bits)
        self.buffer_filename = "%s_values.txt" % (self.module_name())
        self.buffer_module_name = name if name else self.module_name()
        self.test_output_filename = "%s_output_values.txt" % (self.module_name())
        self.write_module()
