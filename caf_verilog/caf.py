import numpy as np
from sk_dsp_comm import digitalcom as dc
from . caf_verilog_base import CafVerilogBase
from . xcorr import XCorr
from . reference_buffer import ReferenceBuffer
from . capture_buffer import CaptureBuffer
from . __version__ import __version__
from jinja2 import Environment, FileSystemLoader, Template
import os
from shutil import copy


class CAF(CafVerilogBase):

    def __init__(self, reference, received, foas,
                 ref_i_bits=12, ref_q_bits=0,
                 rec_i_bits=12, rec_q_bits=0,
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
        self.ref_i_bits = ref_i_bits
        self.ref_q_bits = ref_q_bits if ref_q_bits else self.ref_i_bits
        self.rec_i_bits = rec_i_bits
        self.rec_q_bits = rec_q_bits if rec_q_bits else self.rec_i_bits
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

    def template_dict(self):
        t_dict = {**self.submodules['reference_buffer'].template_dict(),
                  **self.submodules['capture_buffer'].template_dict()}
        return t_dict

    def write_module(self):
        super(CAF, self).write_module()
        params_path = os.path.abspath(os.path.join(self.tb_module_path(), 'caf_state_params.v'))
        copy(params_path, self.output_dir)


def simple_caf(x, y, foas, fs):
    """
    Produce values for a surface plot of the Complex Ambiguity Function.
    This function primarily supports testing values produced via sim_helper, so y is expected to be twice the length of
    x.
    The return is the CAF surface and a time delay range normalized by the sampling frequency.

    :param x: Use x as a reference signal.
    :param y: Use y as a captured signal.
    :param foas: Frequency offsets, provided as a list/iterable object.
    :param fs: Sampling frequency
    :return: caf_res, dt
    """
    nlags = len(x)
    ztup = (nlags, len(foas))
    caf_res = np.zeros(ztup)
    nlen = len(y)
    nrange = np.arange(0, nlen)
    dt_lags = nlags // 2
    dt = np.arange(-dt_lags, dt_lags) / float(fs)
    for k, Df in enumerate(foas):
        theta = np.exp(1j*2*np.pi*nrange*Df/float(fs))
        y_shift = y * theta
        rxy, lags = dc.xcorr(x, y_shift, nlags)
        caf_res[:, k] = np.abs(rxy)
    return caf_res, dt
