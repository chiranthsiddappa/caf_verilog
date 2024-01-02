from .dot_product import DotProduct
import os
from numpy import log2, ceil

filedir = os.path.dirname(os.path.realpath(__file__))
dot_product_tb_module_path = os.path.join(filedir, '..', 'src')
dot_product_module_path = os.path.join(filedir, '..', 'src', 'dot_prod_pip.v')


class DotProdPip(DotProduct):
    """

    """

    def params_dict(self) -> dict:
        t_dict = super().params_dict()
        t_dict['length_counter_bits'] = int(ceil(log2(self.length)))
        return t_dict

    def template_dict(self, inst_name=None):
        t_dict = super(DotProdPip, self).template_dict(inst_name)
        return t_dict


async def capture_test_output_data(dut):
    captured_output = dut.i.value.signed_integer + dut.q.value.signed_integer * 1j
    dut.m_axis_product_tready.value = 1
    if dut.s_axis_product_tvalid.value == 1:
        return captured_output
    else:
        return False


async def send_test_input_data(dut, x, y):

    x_i = int(x.real)
    x_q = int(x.imag)
    y_i = int(y.real)
    y_q = int(y.imag)

    dut.xi.value = x_i
    dut.xq.value = x_q
    dut.yi.value = y_i
    dut.yq.value = y_q
    dut.m_axis_x_tvalid.value = 1
    dut.m_axis_y_tvalid.value = 1
