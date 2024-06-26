import numpy as np

from . caf_verilog_base import CafVerilogBase
from .cpx_multiply import CpxMultiply
from . sig_gen import SigGen, phase_increment, freq_step_str
from jinja2 import Environment, FileSystemLoader, Template
import os
from . quantizer import quantize
from . io_helper import write_quantized_output


async def capture_test_output_data(dut):
    captured_output = dut.i.value.signed_integer + dut.q.value.signed_integer * 1j
    dut.m_axis_tready.value = 1
    if dut.s_axis_tvalid.value == 1:
        return captured_output
    else:
        return False


async def send_test_input_data(dut, x):
    
    assert dut.s_axis_tready.value == 1 # Just to double check
    x_i = int(x.real)
    x_q = int(x.imag)

    dut.xi.value = int(x_i)
    dut.xq.value = int(x_q)
    dut.m_axis_tvalid.value = 1


def freq_res(foas: list) -> float:
    freqs = list()
    for ff in foas:
        if ff:
            freqs.append(abs(ff))
    freqs = np.floor(np.log10(freqs))
    freqs = 10 ** freqs
    min_res = min(freqs)
    return min_res


class FreqShift(CafVerilogBase):

    def __init__(self, x, freq_res, fs, n_bits,
                 i_bits=12, q_bits=0,
                 neg_shift=False, output_dir='.'):
        self.freq_res = freq_res
        self.fs = fs
        self.i_bits = i_bits
        self.q_bits = q_bits if q_bits else self.i_bits
        self.n_bits = n_bits
        self.neg_shift_str = '1\'' + bin(int(neg_shift))[1:]
        self.x_quant = quantize(x, self.i_bits, self.q_bits)
        self.output_dir = output_dir
        self.submodules = {'sig_gen': SigGen(self.freq_res, self.fs, self.n_bits, self.output_dir),
                           'cpx_multiply': CpxMultiply(x=x, y=x, x_i_bits=i_bits, x_q_bits=q_bits, y_i_bits=i_bits, y_q_bits=q_bits,
                                                       output_dir=self.output_dir)}
        self.phase_bits = self.submodules['sig_gen'].phase_bits
        self.tb_filename = '%s_tb.v' % self.module_name()
        self.freq_shift_name = "%s_%s_%s_%s" % (self.module_name(), str(fs).replace('.', '')[:3], self.phase_bits,
                                                self.n_bits)
        self.test_value_filename = '%s_input_values.txt' % (self.freq_shift_name)
        self.test_output_filename = "%s_output_values.txt" % (self.freq_shift_name)
        self.write_module()

    def params_dict(self) -> dict:
        t_dict = dict()
        t_dict['i_bits'] = self.i_bits
        t_dict['q_bits'] = self.q_bits
        t_dict['phase_bits'] = self.phase_bits
        return t_dict

    def template_dict(self):
        t_dict = self.params_dict()
        t_dict['%s_i_bits' % self.module_name()] = self.i_bits
        t_dict['%s_q_bits' % self.module_name()] = self.q_bits
        t_dict['%s_n_bits' % self.module_name()] = self.n_bits
        t_dict['%s_phase_bits' % self.module_name()] = self.phase_bits
        t_dict['neg_shift_str'] = self.neg_shift_str
        t_dict['freq_shift_name'] = self.freq_shift_name
        t_dict['freq_shift_input'] = os.path.abspath(os.path.join(self.output_dir, self.test_value_filename))
        t_dict['freq_shift_output'] = os.path.abspath(os.path.join(self.output_dir, self.test_output_filename))
        sg_t_dict = self.submodules['sig_gen'].template_dict()
        t_dict['sig_gen_name'] = sg_t_dict['sig_gen_name']
        t_dict['sig_gen_inst_name'] = 'fq_sig_gen'
        t_dict['lut_length'] = sg_t_dict['lut_length']
        t_dict['freq_shift_output'] = os.path.abspath(os.path.join(self.output_dir, self.test_output_filename))
        return t_dict

    def write_module(self):
        """
        Generate the module.
        :return:
        """
        t_dict = self.template_dict()
        module_template = None
        with open(self.module_path()) as module_file:
            module_template = Template(module_file.read())
        with open(os.path.join(self.output_dir, self.freq_shift_name+'.v'), "w+") as module_file:
            module_file.write(module_template.render(**t_dict))

    def gen_tb(self, freq=None):
        write_quantized_output(self.output_dir, self.test_value_filename, self.x_quant)
        self.write_freq_shift_tb_module(freq)

    def write_freq_shift_tb_module(self, freq=None):
        des_freq = freq if freq else self.fs / 4
        increment = phase_increment(des_freq, self.phase_bits, self.fs)
        t_dict = self.template_dict()
        t_dict['freq_step_str'] = freq_step_str(self.phase_bits, increment)
        template_loader = FileSystemLoader(searchpath=self.tb_module_path())
        env = Environment(loader=template_loader)
        template = env.get_template(self.tb_filename)
        freq_shift_tb = template.render(**t_dict)
        with open(os.path.join(self.output_dir, self.tb_filename), 'w+') as tb_file:
            tb_file.write(freq_shift_tb)
