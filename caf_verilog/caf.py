import numpy as np
from sk_dsp_comm import digitalcom as dc
from . caf_verilog_base import CafVerilogBase
from . caf_slice import CAFSlice
from . __version__ import __version__
from jinja2 import Environment, FileSystemLoader, Template
import os
from shutil import copy
from . quantizer import quantize
from . io_helper import write_buffer_values
from . quantizer import bin_num
from . sig_gen import phase_increment
from . caf_slice import caf_slice_dot
from . xcorr import gen_tb_values
from math import log2, ceil

try:
    from cocotb.triggers import RisingEdge
except ImportError as ie:
    import warnings
    warnings.warn("Could not import cocotb", ImportWarning)


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
        submodules = {'caf_slice': CAFSlice(reference=self.reference,
                                            received=self.received,
                                            freq_res=self.freq_res(),
                                            ref_i_bits=self.ref_i_bits,
                                            ref_q_bits=self.ref_q_bits,
                                            rec_i_bits=self.rec_i_bits,
                                            rec_q_bits=self.rec_q_bits,
                                            fs=self.fs,
                                            n_bits=self.n_bits,
                                            output_dir=self.output_dir)}
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

    def params_dict(self) -> dict:
        pd = {**self.submodules['caf_slice'].params_dict()}
        num_foas = len(self.foas)
        pd['foas'] = num_foas
        pd['foas_counter_bits'] = int(ceil(log2(num_foas)))
        return pd

    def template_dict(self, inst_name=None):
        t_dict = self.params_dict()
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

    def phase_increment_values(self) -> list:
        phase_bits = self.params_dict()['phase_bits']
        vals = [phase_increment(f_out=abs(freq), phase_bits=phase_bits, f_clk=self.fs) for freq in self.foas]
        return vals

    def write_phase_increment_values(self):
        phase_bits = self.template_dict()['phase_bits']
        with open(os.path.join(self.output_dir, self.phase_increment_filename), 'w+') as pi_file:
            for freq in self.foas:
                incr = phase_increment(abs(freq), phase_bits, self.fs)
                pi_file.write(bin_num(incr, phase_bits) + '\n')
        with open(os.path.join(self.output_dir, self.neg_shift_filename), 'w+') as nn_file:
            for freq in self.foas:
                nn_file.write(str(int(freq < 0)) + '\n')


async def set_increment_values(caf: CAF, dut):
    """

    :param caf: CAF instance to retrieve module values
    :param dut: cocotb design under test
    """
    phase_increments = caf.phase_increment_values()
    neg_shift_vals = np.signbit(caf.foas)

    assert dut.freq_step_index.value == 0

    for inc, bit in zip(phase_increments, neg_shift_vals):
        assert dut.m_axis_freq_step_tready.value == 1
        dut.s_axis_freq_step_tready.value = 1
        dut.freq_step.value = int(inc)
        dut.neg_shift.value = 1 if bit else 0
        dut.s_axis_freq_step_valid.value = 1
        await RisingEdge(dut.clk)

    dut.s_axis_freq_step_tready.value = 0


async def send_input_data(caf: CAF, dut, cycle_timeout=10):
    """
    :param caf: CAF instance to retrieve module values
    :param dut: cocotb design under test
    :param cycle_timeout: Number of clock cycles to wait for ready signal
    """
    ref_tb, rec_tb = gen_tb_values(caf.ref_quant, caf.rec_quant)

    for cycle in range(cycle_timeout):
        if dut.s_axis_tready.value != 1:
            await RisingEdge(dut.clk)

    assert dut.s_axis_tready.value == 1

    for ref_val, rec_val in zip(ref_tb, rec_tb):
        ref_x_i = int(ref_val.real)
        ref_x_q = int(ref_val.imag)
        rec_y_i = int(rec_val.real)
        rec_y_q = int(rec_val.imag)
        dut.m_axis_tvalid.value = 1
        dut.xi.value = ref_x_i
        dut.xq.value = ref_x_q
        dut.yi.value = rec_y_i
        dut.yq.value = rec_y_q
        await RisingEdge(dut.clk)

    dut.m_axis_tvalid.value = 0


async def retrieve_max(caf: CAF, dut, cycle_timeout=20):
    foa_extended_timeout = cycle_timeout + len(caf.foas)
    tvalid_slice_val = (2**(len(caf.foas))) - 1

    dut.m_axis_tvalid.value = 0

    for cycle in range(foa_extended_timeout):
        if dut.s_axis_tvalid_slice.value != tvalid_slice_val:
            await RisingEdge(dut.clk)

    assert dut.s_axis_tvalid_slice.value == tvalid_slice_val

    for cycle in range(foa_extended_timeout):
        if dut.s_axis_tvalid.value != 1:
            await RisingEdge(dut.clk)

    assert dut.s_axis_tvalid.value == 1

    out_max = dut.out_max
    time_index = dut.time_index
    foas_index = dut.foas_index
    dut.m_axis_tready.value = 1

    await RisingEdge(dut.clk)

    dut.m_axis_tready.value = 0

    return int(time_index.value), caf.foas[int(foas_index.value)], int(out_max.value)


def simple_caf(x, y, foas, fs, n_bits=0):
    """
    Produce values for a surface plot of the Complex Ambiguity Function.
    The return is the CAF surface and a time delay range normalized by the sampling frequency.

    :param x: Use x as a reference signal.
    :param y: Use y as a captured signal.
    :param foas: Frequency offsets, provided as a list/iterable object.
    :param fs: Sampling frequency
    :param n_bits: 0 for no quantization on sinusoids
    :return: caf_res, dt
    """
    f_len = len(foas)
    nlags = len(x)
    nlen = len(y)
    nrange = np.arange(0, nlen)
    dt_lags = nlags // 2
    dt = np.arange(-dt_lags, dt_lags) / float(fs)
    caf_res = np.empty([len(foas), nlags])
    theta_shift_range = 1j * 2 * np.pi * nrange / fs
    theta_shifts = np.empty([len(foas), nlen], dtype=np.complexfloating)
    for ff in reversed(range(f_len)):
        theta_shifts[ff] = np.exp(theta_shift_range * foas[ff])
    for ff in range(f_len):
        theta = theta_shifts[ff]
        if n_bits:
            theta = quantize(theta, n_bits)
        x_shift = x * theta
        rxy, lags = dc.xcorr(x_shift, y, nlags)
        caf_res[ff] = np.abs(rxy)
    return caf_res, dt


def dot_caf(x, y, foas, fs, n_bits=0) -> list:
    """
    Produce values for a surface plot of the Complex Ambiguity Function.
    The return is the CAF surface and a time delay range normalized by the sampling frequency.

    :param x: Use x as a reference signal.
    :param y: Use y as a captured signal.
    :param foas: Frequency offsets, provided as a list/iterable object.
    :param fs: Sampling frequency
    :param n_bits: 0 for no quantization on sinusoids.
    """
    res = []
    for fsa in foas:
        res.append(caf_slice_dot(ref=x, rec=y, f_shift=fsa, fs=fs, n_bits=n_bits))
    return res
