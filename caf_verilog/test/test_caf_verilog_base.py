from .. caf_verilog_base import CafVerilogBase
from unittest import TestCase


class TestCafVerilogBase(TestCase):

    def test_instantiation(self):
        CafVerilogBase()

    def test_gen_tb_not_implemented(self):
        cvb = CafVerilogBase()
        with self.assertRaisesRegexp(NotImplementedError, 'This class has not implemented a testbench'):
            cvb.gen_tb()

    def test_template_dict_not_implemented(self):
        cvb = CafVerilogBase()
        with self.assertRaisesRegex(NotImplementedError, "This class has not implemented a template dictionary"):
            cvb.template_dict()