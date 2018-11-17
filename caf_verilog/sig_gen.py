from . quantizer import quantize
import os
from jinja2 import Environment, FileSystemLoader, Template
import numpy as np
from .caf_verilog_base import CafVerilogBase

filedir = os.path.dirname(os.path.realpath(__file__))
sig_gen_tb_module_path = os.path.join(filedir, '..', 'src')
sig_gen_module_path = os.path.join(filedir, '..', 'src', 'sig_gen.v')


class SigGen(CafVerilogBase):

    def __init__(self, freq_res, fs, n_bits, output_dir='.'):
        self.f = freq_res
        self.fs = fs
        self.n_bits = n_bits
        self.phase_bits = phase_bits(fs, freq_res)
        self.output_dir = output_dir
        self.tb_filename = 'sig_gen_tb.v'
        self.sig_gen_name = "sig_gen_%s_%s_%s" % (str(fs).replace('.', '')[:3], self.phase_bits, self.n_bits)
        self.lut_filename = "%s.txt" % (self.sig_gen_name)
        self.test_output_filename = "sig_gen_output_values.txt"
        self.write_module()

    def template_dict(self, inst_name=None):
        t_dict = {'phase_bits': self.phase_bits, 'n_bits': self.n_bits}
        t_dict['lut_filename'] = os.path.abspath(os.path.join(self.output_dir, self.lut_filename))
        t_dict['sig_gen_inst_name'] = inst_name
        t_dict['sig_gen_output'] = os.path.abspath(os.path.join(self.output_dir, self.test_output_filename))
        t_dict['lut_length'] = 2 ** (self.n_bits + 1) - 1
        t_dict['sig_gen_name'] = self.sig_gen_name
        return t_dict

    def gen_tb(self, freq=None):
        """
        Generate a testbench for the specified frequency.

        :param freq:
        :return:
        """
        self.write_sig_gen_tb_module(freq)

    def write_sig_gen_tb_module(self, freq=None):
        """
        Write out a testbench file to test the sig_gen module.

        :param freq:
        :return:
        """
        des_freq = freq if freq else self.fs / 4
        increment = phase_increment(des_freq, self.phase_bits, self.fs)
        t_dict = self.template_dict('sig_gen_tb')
        t_dict['freq_step_str'] = "%d'%s" % (self.phase_bits - 1, str(bin(increment))[1:])
        template_loader = FileSystemLoader(searchpath=sig_gen_tb_module_path)
        env = Environment(loader=template_loader)
        template = env.get_template('sig_gen_tb.v')
        sig_gen_tb = template.render(**t_dict)
        with open(os.path.join(self.output_dir, self.tb_filename), 'w+') as tb_file:
            tb_file.write(sig_gen_tb)

    def write_lut_values(self):
        """

        :return:
        :rtype: None
        """
        values = lut_values(self.n_bits)
        with open(os.path.join(self.output_dir, self.lut_filename), 'w+') as lut_file:
            for val in values:
                lut_file.write(bin_num(val, self.n_bits) + "\n")

    def write_module(self):
        self.write_lut_values()
        module_template = None
        t_dict = self.template_dict()
        with open(sig_gen_module_path) as module_file:
            module_template = Template(module_file.read())
        with open(os.path.join(self.output_dir, self.sig_gen_name+".v"), "w+") as module_file:
            module_file.write(module_template.render(**t_dict))


def lut_values(n_bits):
    """
    Create and return an array of values quantized to the number of bits requested.
    The list is always 2 ** (n_bits + 1) in length for n_bits.

    :param n_bits:
    :return:
    :rtype: list
    """
    step = 2 * np.pi / 2 ** (n_bits + 1)
    n = np.arange(0, 2 * np.pi, step)
    values = np.sin(n)
    values = quantize(values, n_bits)
    return values


def phase_bits(f_clk, freq_res):
    """
    Calculate the number of bits the phase accumulator will need.

    :param f_clk: Sampling rate/clock frequency
    :param freq_res: Frequency resolution required
    :return:
    """
    return int(np.ceil(np.log2(f_clk / freq_res)))


def phase_increment(f_out, phase_bits, f_clk):
    """
    Calculate the phase increment required to produce the desired frequency.

    :param f_out:
    :param phase_bits:
    :param f_clk:
    :return:
    """
    return int(f_out * 2**phase_bits / f_clk)


def bin_num(n, n_bits):
    mask = (2 << n_bits - 1) - 1
    num = int(n) & mask
    f_str = '{:0' + str(n_bits) + 'b}'
    f_res = f_str.format(int(num))
    return f_res
