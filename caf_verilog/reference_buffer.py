from .caf_verilog_base import CafVerilogBase
import os
from . quantizer import quantize
from jinja2 import Environment, FileSystemLoader, Template
from .caf_verilog_base import bin_num

filedir = os.path.dirname(os.path.realpath(__file__))


class ReferenceBuffer(CafVerilogBase):

    def __init__(self, buffer, i_bits=12, q_bits=12, output_dir='.'):
        self.buffer = buffer
        self.i_bits = i_bits
        self.q_bits = q_bits
        self.output_dir = output_dir
        self.buff_quant = quantize(self.buffer, self.i_bits, self.q_bits)
        self.reference_buffer_filename = "%s_values.txt" % (self.module_name())
        self.test_output_filename = "%s_output_values.txt" % (self.module_name())

        self.write_module()

    def write_buffer_values(self):
        """

        :return:
        """
        with open(os.path.join(self.output_dir, self.reference_buffer_filename), 'w+') as rbf:
            for val in self.buff_quant:
                i_bin = bin_num(val.real, self.i_bits)
                q_bin = bin_num(val.imag, self.q_bits)
                rbf.write(i_bin + q_bin + "\n")

    def write_module(self):
        self.write_buffer_values()
