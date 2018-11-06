from . quantizer import quantize
import os
import numpy as np
from jinja2 import Environment, FileSystemLoader, Template
from shutil import copy
from .caf_verilog_base import CafVerilogBase

filedir = os.path.dirname(os.path.realpath(__file__))
dot_product_tb_module_path = os.path.join(filedir, '..', 'src')
dot_product_module_path = os.path.join(filedir, '..', 'src', 'sig_gen.v')


class DotProduct(CafVerilogBase):

    def __init__(self, x, y, x_i_bits=12, x_q_bits=0, y_i_bits=12, y_q_bits=0, output_dir='.'):
        """

        :param x:
        :param y:
        :param x_i_bits:
        :param x_q_bits:
        :param y_i_bits:
        :param y_q_bits:
        :param output_dir:
        """
        self.x = x
        self.y = y
        self.cpx_input_length_check()
        self.length = len(self.x)
        self.x_i_bits = x_i_bits
        self.x_q_bits = x_q_bits if x_q_bits else self.x_i_bits
        self.y_i_bits = y_i_bits
        self.y_q_bits = y_q_bits if y_q_bits else self.y_i_bits
        self.sum_i_size = np.log2(x_i_bits * self.length) if x_i_bits > y_i_bits else np.log2(y_i_bits * self.length)
        self.sum_q_size = np.log2(x_q_bits * self.length) if x_q_bits > y_q_bits else np.log2(y_q_bits * self.length)
        self.x_quant = quantize(self.x, self.x_i_bits, self.x_q_bits)
        self.y_quant = quantize(self.y, self.y_i_bits, self.y_q_bits)
        self.output_dir = output_dir
        self.tb_filename = 'dot_product_tb.v'
        self.test_value_filename = 'dot_product_input_values.txt'
        self.test_output_filename = 'dot_product_output_values.txt'
        copy(dot_product_module_path, self.output_dir)

    def template_dict(self):
        t_dict = {'xi_bits': self.x_i_bits, 'xq_bits': self.x_q_bits, 'yi_bits': self.y_i_bits,
                  'yq_bits': self.y_q_bits, 'length': self.length, 'sum_i_size': self.sum_i_size,
                  'sum_q_size': self.sum_q_size}