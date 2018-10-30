from . quantizer import quantize
from . io_helper import write_quantized_output
import os
import numpy as np

filedir = os.path.dirname(os.path.realpath(__file__))
cpx_multiply_tb_module_path = os.path.join(filedir, '..', 'src')
cpx_multiply_path = os.path.join(filedir, '..', 'src', 'cpx_multiply.v')


class SigGen:

    def __init__(self, freq_res, fs, n_bits, output_dir='.'):
        self.f = freq_res
        self.fs = fs
        self.n_bits = n_bits
        self.phase_bits = phase_bits(fs, freq_res)
        self.output_dir = output_dir

    def template_dict(self):
        t_dict = {'phase_bits': self.phase_bits, 'n_bits': self.n_bits}


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