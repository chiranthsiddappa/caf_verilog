from .caf_verilog_base import CafVerilogBase
import os
from . quantizer import quantize
from jinja2 import Environment, FileSystemLoader, Template
from caf_verilog.quantizer import bin_num
import numpy as np

filedir = os.path.dirname(os.path.realpath(__file__))


class ReferenceBuffer(CafVerilogBase):

    def __init__(self, buffer, i_bits=12, q_bits=12, output_dir='.', name=None):
        self.buffer = buffer
        self.i_bits = i_bits
        self.q_bits = q_bits
        self.output_dir = output_dir
        self.tb_filename = '%s_tb.v' % (self.module_name())
        self.buff_quant = quantize(self.buffer, self.i_bits, self.q_bits)
        self.reference_buffer_filename = "%s_values.txt" % (self.module_name())
        self.reference_buffer_module_name = name if name else self.module_name()
        self.test_output_filename = "%s_output_values.txt" % (self.module_name())
        self.module_path = os.path.join(filedir, '..', 'src', '%s.v' % (self.module_name()))
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
        module_template = None
        t_dict = self.template_dict()
        with open(self.module_path) as module_file:
            module_template = Template(module_file.read())
        with open(os.path.join(self.output_dir, self.module_name()+".v"), 'w+') as module_file:
            module_file.write(module_template.render(**t_dict))

    def template_dict(self):
        b_len = len(self.buffer)
        bits = int(np.ceil(np.log2(b_len)))
        t_dict = {'buffer_length': b_len, 'index_bits': bits,'i_bits': self.i_bits, 'q_bits': self.q_bits}
        rbf_path = os.path.join(self.output_dir, self.reference_buffer_filename)
        t_dict['reference_buffer_filename'] = os.path.abspath(rbf_path)
        t_dict['reference_buffer_name'] = self.reference_buffer_module_name
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
