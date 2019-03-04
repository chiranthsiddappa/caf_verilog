from .dot_product import DotProduct
import os
from numpy import log2

filedir = os.path.dirname(os.path.realpath(__file__))
dot_product_tb_module_path = os.path.join(filedir, '..', 'src')
dot_product_module_path = os.path.join(filedir, '..', 'src', 'dot_prod_pip.v')


class DotProdPip(DotProduct):
    """

    """

    def template_dict(self, inst_name=None):
        t_dict = {'xi_bits': self.x_i_bits, 'xq_bits': self.x_q_bits, 'yi_bits': self.y_i_bits,
                  'yq_bits': self.y_q_bits, 'length': self.length, 'length_counter_size': int(log2(self.length)),
                  'sum_i_size': self.sum_i_size, 'sum_q_size': self.sum_q_size}
        t_dict['dot_prod_input'] = os.path.abspath(os.path.join(self.output_dir, self.test_value_filename))
        t_dict['dot_prod_output'] = os.path.abspath(os.path.join(self.output_dir, self.test_output_filename))
        t_dict['dot_prod_name'] = inst_name if inst_name else 'dot_prod_tb'
        return t_dict
