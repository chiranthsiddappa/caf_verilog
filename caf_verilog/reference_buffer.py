from .caf_verilog_base import CafVerilogBase
import os
from . quantizer import quantize
from jinja2 import Environment, FileSystemLoader, Template
from . io_helper import write_buffer_values
import numpy as np

filedir = os.path.dirname(os.path.realpath(__file__))


class ReferenceBuffer(CafVerilogBase):

    def __init__(self, buffer, i_bits=12, q_bits=0, output_dir='.', name=None):
        self.buffer = buffer
        self.i_bits = i_bits
        self.q_bits = q_bits if q_bits else self.i_bits
        self.output_dir = output_dir
        self.tb_filename = '%s_tb.v' % (self.module_name())
        self.buffer_quant = quantize(self.buffer, self.i_bits, self.q_bits)
        self.buffer_filename = "%s_values.txt" % (self.module_name())
        self.buffer_module_name = name if name else self.module_name()
        self.test_output_filename = "%s_output_values.txt" % (self.module_name())
        self.write_module()

    def write_module(self):
        write_buffer_values(self.output_dir, self.buffer_filename, self.buffer_quant, self.i_bits, self.q_bits)
        module_template = None
        t_dict = self.template_dict()
        with open(self.module_path()) as module_file:
            module_template = Template(module_file.read())
        with open(os.path.join(self.output_dir, self.module_name()+".v"), 'w+') as module_file:
            module_file.write(module_template.render(**t_dict))

    def template_dict(self):
        b_len = len(self.buffer)
        bits = int(np.ceil(np.log2(b_len)))
        mn = self.module_name().split('_')[0][:3]
        t_dict = dict()
        t_dict['%s_buffer_length' % mn] = b_len
        t_dict['%s_index_bits' % mn] = bits
        t_dict['%s_i_bits' % mn] = self.i_bits
        t_dict['%s_q_bits' % mn] = self.q_bits
        rbf_path = os.path.join(self.output_dir, self.buffer_filename)
        t_dict['%s_filename' % self.module_name()] = os.path.abspath(rbf_path)
        t_dict['%s_name' % self.module_name()] = self.buffer_module_name
        t_dict['test_output_filename'] = os.path.abspath(os.path.join(self.output_dir, self.test_output_filename))
        return t_dict

    def gen_tb(self):
        t_dict = self.template_dict()
        template_loader = FileSystemLoader(searchpath=self.tb_module_path())
        env = Environment(loader=template_loader)
        template = env.get_template(self.tb_filename)
        ref_buff_tb = template.render(**t_dict)
        with open(os.path.join(self.output_dir, self.tb_filename), 'w+') as tb_file:
            tb_file.write(ref_buff_tb)
