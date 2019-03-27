from . caf_verilog_base import CafVerilogBase
from . sig_gen import phase_bits, SigGen
from jinja2 import Environment, FileSystemLoader, Template
import os


class FreqShift(CafVerilogBase):

    def __init__(self, x, freq_res, fs, n_bits, i_bits=12, q_bits=12, output_dir='.'):
        self.freq_res = freq_res
        self.fs = fs
        self.i_bits = i_bits
        self.q_bits = q_bits if q_bits else 0
        self.n_bits = n_bits
        self.output_dir = output_dir
        self.submodules = {'sig_gen': SigGen(self.freq_res, self.fs, self.n_bits, self.output_dir)}
        self.phase_bits = self.submodules['sig_gen'].phase_bits
        self.tb_filename = '%s_tb.v' % self.module_name()
        self.freq_shift_name = "%s_%s_%s_%s" % (self.module_name(), str(fs).replace('.', '')[:3], self.phase_bits,
                                                self.n_bits)

    def template_dict(self):
        t_dict = {'i_bits': self.i_bits, 'q_bits': self.q_bits, 'n_bits': self.n_bits, 'phase_bits': self.phase_bits}
        t_dict['freq_shift_name'] = self.freq_shift_name
        sg_t_dict = self.submodules['sig_gen'].template_dict()
        t_dict['sig_gen_name'] = sg_t_dict['sig_gen_name']
        t_dict['sig_gen_inst_name'] = 'fq_sig_gen'
        t_dict['lut_length'] = sg_t_dict['lut_length']
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
