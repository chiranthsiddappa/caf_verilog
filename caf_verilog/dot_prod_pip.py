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
