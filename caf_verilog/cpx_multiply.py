from .quantizer import quantize
from .io_helper import write_quantized_output
from numpy import floor
import os
from jinja2 import Environment, FileSystemLoader
from shutil import copy

filedir = os.path.dirname(os.path.realpath(__file__))
cpx_multiply_tb_module_path = os.path.join(filedir, '..', 'src')
cpx_multiply_path = os.path.join(filedir, '..', 'src', 'cpx_multiply.v')


class CpxMultiply:

    def __init__(self, x, y, x_i_bits=12, x_q_bits=0, y_i_bits=12, y_q_bits=0, output_dir='.'):
        """

        :param x:
        :param y:
        :param x_i_bits: Bit length for real values
        :param x_q_bits: Bit length for imaginary values
        :param y_i_bits: Bit length for real values
        :param y_q_bits: Bit length for imaginary values
        :param output_dir: Directory to place modules and test files
        """
        self.x = x
        self.y = y
        if not (len(self.x) == len(self.y)):
            raise ValueError("x and y are not the same length")
        self.x_i_bits = x_i_bits
        self.x_q_bits = x_q_bits if x_q_bits else self.x_i_bits
        self.y_i_bits = y_i_bits
        self.y_q_bits = y_q_bits if y_q_bits else self.y_i_bits
        self.x_quant = quantize(self.x, self.x_i_bits, self.x_q_bits)
        self.y_quant = quantize(self.y, self.y_i_bits, self.y_q_bits)
        self.output_dir = output_dir
        self.tb_filename = 'cpx_multiply_tb.v'
        self.test_value_filename = 'cpx_multiply_input_values.txt'
        self.test_output_filename = 'cpx_multiply_output_values.txt'

    def gen_tb(self):
        """
        Generate a test bench using quantized values.

        :return:
        """
        write_quantized_output(self.output_dir, self.test_value_filename, self.x_quant, self.y_quant)
        self.write_cpx_multiply_tb_module()
        copy(cpx_multiply_path, self.output_dir)

    def gen_quantized_output(self):
        """
        Perform the multiplication and then quantize to the closest representation of what the verilog module should
        produce for the given bit length.

        :return:
        """
        """
           x       y
        (x + yi)(u + vi) = (xu - yv) + (xv + yu)i
        """
        xu = floor(self.x_quant.real) * floor(self.y_quant.real)
        yv = floor(self.x_quant.imag) * floor(self.y_quant.imag)
        xv = floor(self.x_quant.real) * floor(self.y_quant.imag)
        yu = floor(self.x_quant.imag) * floor(self.y_quant.real)
        i_sub = xu - yv
        y_add = xv + yu
        final_out = i_sub + y_add*1j
        return final_out

    def write_cpx_multiply_tb_module(self):
        """
        Write out a testbench file to test the cpx_multiply module.

        :return:
        """
        out_tb = None
        t_dict = self.template_dict()
        template_loader = FileSystemLoader(searchpath=cpx_multiply_tb_module_path)
        env = Environment(loader=template_loader)
        template = env.get_template('cpx_multiply_tb.v')
        out_tb = template.render(**t_dict)
        with open(os.path.join(self.output_dir, self.tb_filename), 'w+') as tb_file:
            tb_file.write(out_tb)

    def template_dict(self):
        t_dict = {'xi_bits': self.x_i_bits, 'xq_bits': self.x_q_bits, 'yi_bits': self.y_i_bits,
                  'yq_bits': self.y_q_bits}
        t_dict['i_out_bits'] = self.x_i_bits + self.y_i_bits
        t_dict['q_out_bits'] = self.x_q_bits + self.y_q_bits
        t_dict['cpx_multiply_input'] = os.path.abspath(os.path.join(self.output_dir, self.test_value_filename))
        t_dict['cpx_multiply_output'] = os.path.abspath(os.path.join(self.output_dir, self.test_output_filename))
        return t_dict
