import numpy as np
from sk_dsp_comm import digitalcom as dc
from . caf_verilog_base import CafVerilogBase
from . xcorr import XCorr
from . reference_buffer import ReferenceBuffer
from . capture_buffer import CaptureBuffer
from . freq_shift import FreqShift
from . __version__ import __version__
from jinja2 import Environment, FileSystemLoader, Template
import os
from shutil import copy
from . quantizer import quantize
from . io_helper import write_buffer_values
from . quantizer import bin_num
from . sig_gen import phase_increment
from math import log2, ceil


class CAF(CafVerilogBase):

    def __init__(self, reference, received, foas,
                 ref_i_bits=12, ref_q_bits=0,
                 rec_i_bits=12, rec_q_bits=0,
                 fs=625e3, n_bits=8,
                 pipeline=True, output_dir='.'):
        """

        :param reference:
        :param received:
        :param ref_i_bits:
        :param ref_q_bits:
        :param output_dir:
        """
        self.reference = reference
        self.received = received
        if not len(self.reference) == (len(self.received) / 2):
            raise ValueError("Received signal must be twice the length of the reference signal")
        self.foas = foas
        self.fs = fs
        self.n_bits = n_bits
        self.ref_i_bits = ref_i_bits
        self.ref_q_bits = ref_q_bits if ref_q_bits else self.ref_i_bits
        self.rec_i_bits = rec_i_bits
        self.rec_q_bits = rec_q_bits if rec_q_bits else self.rec_i_bits
        self.ref_quant = quantize(self.reference, self.ref_i_bits, self.ref_q_bits)
        self.rec_quant = quantize(self.received, self.rec_i_bits, self.rec_q_bits)
        self.test_value_filename = '%s_input_values.txt' % (self.module_name())
        self.test_output_filename = '%s_output_values.txt' % (self.module_name())
        self.phase_increment_filename = '%s_phase_increment_values.txt' % self.module_name()
        self.neg_shift_filename = '%s_neg_shift_values.txt' % self.module_name()
        self.pip = pipeline
        if not self.pip:
            raise NotImplementedError("A non-pipelined dot-product has not been implemented as of %s" % __version__)
        self.output_dir = output_dir
        self.submodules = self.gen_submodules()
        self.write_module()

    def gen_submodules(self):
        submodules = dict()
        submodules['reference_buffer'] = ReferenceBuffer(self.reference, self.ref_i_bits, self.ref_q_bits,
                                                 self.output_dir, 'ref')
        submodules['capture_buffer'] = CaptureBuffer(len(self.received), self.rec_i_bits, self.rec_q_bits,
                                               self.output_dir, 'cap')
        submodules['freq_shift'] = FreqShift(self.received, self.freq_res(), self.fs, self.n_bits,
                                             i_bits=self.rec_i_bits, q_bits=self.rec_q_bits,
                                             output_dir=self.output_dir)
        submodules['x_corr'] = XCorr(self.reference, self.received, self.ref_i_bits, self.ref_q_bits,
                                     self.rec_i_bits, self.rec_q_bits, pipeline=self.pip, output_dir=self.output_dir)
        return submodules

    def freq_res(self):
        freqs = list()
        for ff in self.foas:
            if ff:
                freqs.append(abs(ff))
        freqs = np.floor(np.log10(freqs))
        freqs = 10 ** freqs
        min_res = min(freqs)
        return min_res

    def template_dict(self, inst_name=None):
        t_dict = {**self.submodules['reference_buffer'].template_dict(),
                  **self.submodules['capture_buffer'].template_dict(),
                  **self.submodules['freq_shift'].template_dict(),
                  **self.submodules['x_corr'].template_dict()}
        t_dict['%s_foa_len' % self.module_name()] = len(self.foas)
        t_dict['%s_foa_len_bits' % self.module_name()] = int(ceil(log2(len(self.foas))))
        t_dict['%s_phase_increment_filename' % self.module_name()] = os.path.abspath(os.path.join(self.output_dir,
                                                                             self.phase_increment_filename))
        t_dict['%s_neg_shift_filename' % self.module_name()] = os.path.abspath(os.path.join(self.output_dir,
                                                                               self.neg_shift_filename))
        t_dict['%s_input' % self.module_name()] = os.path.abspath(os.path.join(self.output_dir,
                                                                               self.test_value_filename))
        t_dict['%s_name' % self.module_name()] = inst_name if inst_name else '%s_tb' % self.module_name()
        return t_dict

    def write_module(self):
        super(CAF, self).write_module()
        params_path = os.path.abspath(os.path.join(self.tb_module_path(), 'caf_state_params.v'))
        self.write_phase_increment_values()
        copy(params_path, self.output_dir)

    def gen_tb(self):
        write_buffer_values(self.output_dir, self.test_value_filename, self.rec_quant, self.rec_i_bits, self.rec_q_bits)
        self.write_tb_module()

    def write_tb_module(self):
        t_dict = self.template_dict()
        template_loader = FileSystemLoader(searchpath=self.tb_module_path())
        env = Environment(loader=template_loader)
        template = env.get_template('%s_tb.v' % self.module_name())
        out_tb = template.render(**t_dict)
        with open(os.path.join(self.output_dir, '%s_tb.v' % self.module_name()), 'w+') as tb_file:
            tb_file.write(out_tb)

    def write_phase_increment_values(self):
        phase_bits = self.template_dict()['freq_shift_phase_bits']
        with open(os.path.join(self.output_dir, self.phase_increment_filename), 'w+') as pi_file:
            for freq in self.foas:
                incr = phase_increment(abs(freq), phase_bits, self.fs)
                pi_file.write(bin_num(incr, phase_bits) + '\n')
        with open(os.path.join(self.output_dir, self.neg_shift_filename), 'w+') as nn_file:
            for freq in self.foas:
                nn_file.write(str(int(freq < 0)) + '\n')


def simple_caf(x, y, foas, fs):
    """
    Produce values for a surface plot of the Complex Ambiguity Function.
    The return is the CAF surface and a time delay range normalized by the sampling frequency.

    :param x: Use x as a reference signal.
    :param y: Use y as a captured signal.
    :param foas: Frequency offsets, provided as a list/iterable object.
    :param fs: Sampling frequency
    :return: caf_res, dt
    """
    nlags = len(x)
    ztup = (nlags, len(foas))
    caf_res = []
    nlen = len(y)
    nrange = np.arange(0, nlen)
    dt_lags = nlags // 2
    dt = np.arange(-dt_lags, dt_lags) / float(fs)
    for k, Df in enumerate(reversed(foas)):
        theta = np.exp(1j*2*np.pi*nrange*Df/float(fs))
        y_shift = y * theta
        rxy, lags = dc.xcorr(x, y_shift, nlags)
        caf_res.append(np.abs(rxy))
    return caf_res, dt
