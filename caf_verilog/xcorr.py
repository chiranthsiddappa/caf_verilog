from . caf_verilog_base import CafVerilogBase
from .quantizer import quantize
from . dot_product import dot_product
import os
from jinja2 import Environment, FileSystemLoader, Template
from . arg_max import ArgMax
from . dot_prod_pip import DotProdPip
from . dot_product import DotProduct
from .io_helper import write_quantized_output


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
        submodules['arg_max'] = ArgMax(self.ref,
                                       dp_dict['sum_i_bits'],
                                       dp_dict['sum_q_bits'],
                                       self.output_dir)
        return submodules

    def template_dict(self, inst_name=None):
        t_dict = self.submodules['dot_prod'].template_dict('dp_x_corr')
        am_dict = self.submodules['arg_max'].template_dict()
        t_dict['out_max_bits'] = am_dict['out_max_bits']
        lcb = 'length_counter_bits'
        if not lcb in t_dict:
            t_dict[lcb] = am_dict['index_bits']
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
        ref_tb = list()
        rec_tb = list()
        for i in range(0, len(self.rec_quant) - len(self.ref_quant) + 1):
            ref_tb.extend(self.ref_quant)
            rec_tb.extend(self.rec_quant[i:len(self.ref_quant) + i])
        write_quantized_output(self.output_dir, self.test_value_filename, ref_tb, rec_tb)


    def gen_quantized_output(self):
        """

        :return:
        """


def dot_xcorr(ref, rec):
    """
    Perform the cross correlation using the dot product.
    This produces an output list of magnitudes that are inverse offset from the center
    of the reference signal.

    :param ref:
    :param rec:
    :return:
    """
    dx = []
    for i in range(0, len(rec) - len(ref) + 1):
        dx.append(dot_product(ref, rec[i:len(ref) + i]))
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
        sum = 0
        for m in range(0, len(g)):
            cc_index = m + n
            if cc_index >= 0 and cc_index < len(g):
                sum += f[m] * g[cc_index]
        sums.append(sum)
    return sums, space


def size_visualization(f, g, nlags):
    space = range(-nlags, nlags + 1)
    for n in space:
        n_indexes = []
        for m in range(0, len(g)):
            cc_index = m + n
            if cc_index >= 0 and cc_index < len(g):
                n_indexes.append((m, cc_index))
        spacing = " " * int(n >= 0)
        print("n: " + spacing + str(n) + " " + str(n_indexes))
