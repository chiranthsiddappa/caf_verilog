from .caf_verilog_base import CafVerilogBase
from .quantizer import quantize
from .dot_product import dot_product
from .arg_max import ArgMax
from .dot_prod_pip import DotProdPip
from .dot_product import DotProduct
from .io_helper import write_quantized_output

import numpy as np
import os
from jinja2 import Environment, FileSystemLoader, Template
from typing import Iterable

try:
    from cocotb.triggers import RisingEdge
except ImportError as ie:
    import warnings
    warnings.warn("Could not import cocotb", ImportWarning)


class XCorr(CafVerilogBase):

    def __init__(self, ref, rec,
                 ref_i_bits=12, ref_q_bits=0,
                 rec_i_bits=12, rec_q_bits=0,
                 pipeline=True, output_dir='.'):
        """

        :param ref: Reference signal.
        :param rec: Received or simulated secondary signal.
        :param ref_i_bits:
        :param ref_q_bits:
        :param rec_i_bits:
        :param rec_q_bits:
        :param pipeline:
        """
        self.ref = ref
        self.rec = rec
        self.ref_i_bits = ref_i_bits
        self.ref_q_bits = ref_q_bits if ref_q_bits else ref_i_bits
        self.rec_i_bits = rec_i_bits
        self.rec_q_bits = rec_q_bits if rec_q_bits else rec_i_bits
        self.ref_quant = quantize(self.ref, self.ref_i_bits, self.ref_q_bits)
        self.rec_quant = quantize(self.rec, self.rec_i_bits, self.rec_q_bits)
        self.pip = pipeline
        self.output_dir = output_dir
        self.tb_filename = '%s_tb.v' % self.module_name()
        self.test_value_filename = '%s_input_values.txt' % self.module_name()
        self.test_output_filename = '%s_output_values.txt' % self.module_name()
        self.ref_quant = quantize(self.ref, self.ref_i_bits, self.ref_q_bits)
        self.rec_quant = quantize(self.rec, self.rec_i_bits, self.rec_q_bits)
        self.submodules = self.gen_submodules()
        self.write_module()

    def gen_submodules(self):
        submodules = dict()
        dp_params = {'x': self.ref, 'y': self.ref,
                     'x_i_bits': self.ref_i_bits, 'x_q_bits': self.ref_q_bits,
                     'y_i_bits': self.rec_i_bits, 'y_q_bits': self.ref_q_bits,
                     'output_dir': self.output_dir}
        if self.pip:
            submodules['dot_prod'] = DotProdPip(**dp_params)
        else:
            submodules['dot_prod'] = DotProduct(**dp_params)
        dp_dict = submodules['dot_prod'].template_dict('dot_prod_%s' % (self.module_name()))
        argmax_ref_vector = np.array(list(self.ref) + [0, 0])
        submodules['arg_max'] = ArgMax(argmax_ref_vector,
                                       dp_dict['sum_i_bits'],
                                       dp_dict['sum_q_bits'],
                                       self.output_dir)
        return submodules

    def params_dict(self) -> dict:
        t_dict = self.submodules['dot_prod'].params_dict()
        am_dict = self.submodules['arg_max'].params_dict()
        del t_dict['sum_i_bits']
        del t_dict['sum_q_bits']
        del t_dict['dot_length']
        del t_dict['dot_length_counter_bits']
        t_dict['out_max_bits'] = am_dict['out_max_bits']
        lcb = 'length_counter_bits'
        if not lcb in t_dict:
            t_dict[lcb] = am_dict['index_bits']
        t_dict['length'] = am_dict['buffer_length']
        return t_dict

    def template_dict(self, inst_name=None):
        t_dict = self.submodules['dot_prod'].template_dict('dp_x_corr') | self.params_dict()
        t_dict['x_corr_inst_name'] = inst_name if inst_name else '%s_tb' % self.module_name()
        t_dict['x_corr_input_filename'] = os.path.abspath(os.path.join(self.output_dir, self.test_value_filename))
        return t_dict

    def gen_tb(self):
        self.write_tb_values()
        self.write_xcorr_tb_module()

    def write_xcorr_tb_module(self):
        t_dict = self.template_dict()
        template_loader = FileSystemLoader(searchpath=self.tb_module_path())
        env = Environment(loader=template_loader)
        template = env.get_template(self.tb_filename)
        out_tb = template.render(**t_dict)
        with open(os.path.join(self.output_dir, self.tb_filename), 'w+') as tb_file:
            tb_file.write(out_tb)

    def write_tb_values(self):
        ref_tb, rec_tb = gen_tb_values(self.ref_quant, self.rec_quant)
        write_quantized_output(self.output_dir, self.test_value_filename, ref_tb, rec_tb)

    def gen_quantized_output(self):
        """

        :return:
        """


def gen_tb_values(ref, rec):
    """
    Reference and received vectors to be provided to the module.
    Copies the ref vector by the length of the ref vector.
    Received vector is shifted in by a positive offset each time.
    """
    ref_tb = list()
    rec_tb = list()
    ref_len = len(ref)
    for i in range(0, len(rec) - ref_len + 1):
        ref_tb.extend(ref)
        rec_tb.extend(rec[i:ref_len + i])
    return ref_tb, rec_tb


def dot_xcorr(ref, rec) -> list:
    """
    Perform the cross correlation using the dot product.
    This produces an output list of magnitudes that are inverse offset from the center
    of the reference signal.

    :param ref:
    :param rec:
    :return:
    """
    dx = []
    ref_len = len(ref)
    for i in range(0, len(rec) - ref_len + 1):
        dx.append(dot_product(ref, rec[i:ref_len + i]))
    return dx


def simple_xcorr(f, g, nlags):
    """

    :param f:
    :param g:
    :param nlags:
    :return:
    """
    sums = []
    space = range(-nlags, nlags + 1)
    for n in space:
        nth_sum = 0
        for m in range(0, len(g)):
            cc_index = m + n
            if 0 <= cc_index < len(g):
                nth_sum += f[m] * g[cc_index]
        sums.append(nth_sum)
    return sums, space


def size_visualization(f, g, nlags):
    space = range(-nlags, nlags + 1)
    for n in space:
        n_indexes = []
        for m in range(0, len(g)):
            cc_index = m + n
            if 0 <= cc_index < len(g):
                n_indexes.append((m, cc_index))
        spacing = " " * int(n >= 0)
        print("n: " + spacing + str(n) + " " + str(n_indexes))


async def capture_test_output_data(dut, cycle_timeout=10) -> tuple:
    """
    This method will wait for signal s_axis_tvalid to become 1, and then return the out_max and index values.
    """
    for cycle in range(cycle_timeout):
        captured_out_max = dut.out_max.value
        captured_index = dut.index.value
        dut.m_axis_tready.value = 1
        if dut.s_axis_tvalid.value == 1:
            return captured_out_max, captured_index
        await RisingEdge(dut.clk)
    raise RuntimeError("Could not retrieve result in %d cycles" % cycle_timeout)


async def send_test_input_data(dut, x, y):

    x_i = int(x.real)
    x_q = int(x.imag)
    y_i = int(y.real)
    y_q = int(y.imag)

    dut.xi.value = x_i
    dut.xq.value = x_q
    dut.yi.value = y_i
    dut.yq.value = y_q
    dut.m_axis_tvalid.value = 1


async def send_and_receive(dut, ref_vals: Iterable, rec_vals: Iterable, cycle_timeout=10) -> tuple:
    """

    :param dut: Design Under Test
    :param ref_vals: List of reference values
    :param rec_vals: List of received values
    """
    output_cap = []
    for ref_cpx_val, rec_cpx_val in zip(ref_vals, rec_vals):
        assert dut.s_axis_tready.value == 1
        dut.m_axis_tready.value = 1
        await send_test_input_data(dut, ref_cpx_val, rec_cpx_val)
        await RisingEdge(dut.clk)

    await RisingEdge(dut.clk)
    dut.m_axis_tvalid.value = 0

    output_max, captured_index = await capture_test_output_data(dut, cycle_timeout=cycle_timeout)

    return output_max, captured_index
