from . caf_verilog_base import CafVerilogBase
import os
import numpy as np
from . quantizer import quantize
from . io_helper import write_quantized_output
from shutil import copy
from jinja2 import Environment, FileSystemLoader


class ArgMax(CafVerilogBase):

    def __init__(self, x, i_bits=12, q_bits=None, output_dir='.'):
        self.x = x
        self.i_bits = i_bits
        self.q_bits = q_bits if q_bits else i_bits
        self.x_quant = quantize(self.x, self.i_bits, self.q_bits)
        self.buffer_length = len(self.x) + 1
        self.index_bits = int(np.ceil(np.log2(self.buffer_length))) + 1
        self.output_dir = output_dir
        self.tb_filename = '%s_tb.v' % (self.module_name())
        self.test_value_filename = '%s_input_values.txt' % (self.module_name())
        self.test_output_filename = '%s_output_values.txt' % (self.module_name())
        copy(self.module_path(), self.output_dir)

    def gen_tb(self):
        write_quantized_output(self.output_dir, self.test_value_filename, self.x_quant)
        self.write_arg_max_tb_module()

    def write_arg_max_tb_module(self):
        out_tb = None
        t_dict = self.template_dict()
        template_loader = FileSystemLoader(searchpath=self.tb_module_path())
        env = Environment(loader=template_loader)
        template = env.get_template(self.tb_filename)
        out_tb = template.render(**t_dict)
        with open(os.path.join(self.output_dir, self.tb_filename), 'w+') as tb_file:
            tb_file.write(out_tb)

    def template_dict(self):
        t_dict = {'i_bits': self.i_bits, 'q_bits': self.q_bits, 'arg_max_index_bits': self.index_bits,}
        t_dict['arg_max_buffer_length'] = self.buffer_length
        t_dict['out_max_bits'] = int((self.i_bits + self.q_bits) / 2)
        t_dict['arg_max_input'] = os.path.abspath(os.path.join(self.output_dir, self.test_value_filename))
        t_dict['arg_max_output'] = os.path.abspath(os.path.join(self.output_dir, self.test_output_filename))
        return t_dict

    def gen_quantized_argsum(self):
        argsum = (self.x_quant.real ** 2) + (self.x_quant.imag ** 2)
        return argsum
