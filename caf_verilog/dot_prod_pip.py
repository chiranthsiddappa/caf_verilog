from .dot_product import DotProduct
import os

filedir = os.path.dirname(os.path.realpath(__file__))
dot_product_tb_module_path = os.path.join(filedir, '..', 'src')
dot_product_module_path = os.path.join(filedir, '..', 'src', 'dot_prod_pip.v')


class DotProdPip(DotProduct):
    """

    """