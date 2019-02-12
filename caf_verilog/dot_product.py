from . quantizer import quantize
import os
import numpy as np
from jinja2 import Environment, FileSystemLoader, Template
from shutil import copy
from .caf_verilog_base import CafVerilogBase
from .io_helper import write_quantized_output

filedir = os.path.dirname(os.path.realpath(__file__))
dot_product_tb_module_path = os.path.join(filedir, '..', 'src')


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
        if self.x_i_bits > self.y_i_bits:
            self.sum_i_size = ((2**self.x_i_bits - 1)**2) * self.length
        else:
            self.sum_i_size = ((2**self.y_i_bits - 1)**2) * self.length
        self.sum_i_size = int(np.ceil(np.log2(self.sum_i_size)))
        if self.x_q_bits > self.y_q_bits:
            self.sum_q_size = ((2**self.x_q_bits - 1)**2) * self.length
        else:
            self.sum_q_size = ((2**self.y_q_bits - 1)**2) * self.length
        self.sum_q_size = int(np.ceil(np.log2(self.sum_q_size)))
        self.x_quant = quantize(self.x, self.x_i_bits, self.x_q_bits)
        self.y_quant = quantize(self.y, self.y_i_bits, self.y_q_bits)
        self.output_dir = output_dir
        dot_product_module_path = os.path.join(filedir, '..', 'src', '%s.v' % (self.module_name()))
        self.tb_filename = '%s_tb.v' % (self.module_name())
        self.test_value_filename = '%s_input_values.txt' % (self.module_name())
        self.test_output_filename = '%s_output_values.txt' % (self.module_name())
        copy(dot_product_module_path, self.output_dir)

    def gen_tb(self):
        write_quantized_output(self.output_dir, self.test_value_filename, self.x_quant, self.y_quant)
        self.write_dot_product_tb_module()

    def template_dict(self, inst_name=None):
        t_dict = {'xi_bits': self.x_i_bits, 'xq_bits': self.x_q_bits, 'yi_bits': self.y_i_bits,
                  'yq_bits': self.y_q_bits, 'length': self.length, 'sum_i_size': self.sum_i_size,
                  'sum_q_size': self.sum_q_size}
        t_dict['dot_prod_input'] = os.path.abspath(os.path.join(self.output_dir, self.test_value_filename))
        t_dict['dot_prod_output'] = os.path.abspath(os.path.join(self.output_dir, self.test_output_filename))
        t_dict['dot_prod_name'] = inst_name if inst_name else 'dot_prod_tb'
        return t_dict

    def write_dot_product_tb_module(self):
        """
        Write out a testbench file to test the dot_product module.

        :return:
        """
        out_tb = None
        t_dict = self.template_dict("%s_tb" % (self.module_name()))
        template_loader = FileSystemLoader(searchpath=dot_product_tb_module_path)
        env = Environment(loader=template_loader)
        template = env.get_template('%s_tb.v' % (self.module_name()))
        out_tb = template.render(**t_dict)
        with open(os.path.join(self.output_dir, self.tb_filename), 'w+') as tb_file:
            tb_file.write(out_tb)
