import inflection
import os


class CafVerilogBase:

    def gen_tb(self):
        raise NotImplementedError("This class has not implemented a testbench")

    def template_dict(self):
        raise NotImplementedError("This class has not implemented a template dictionary")

    def cpx_input_length_check(self):
        if not (len(self.x) == len(self.y)):
            raise ValueError("x and y are not the same length")

    def module_name(self):
        return inflection.underscore(type(self).__name__)

    def tb_module_path(self):
        filedir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(filedir, '..', 'src')
        return path

    def module_path(self):
        v_module_name = self.module_name() + '.v'
        vmp = os.path.join(self.tb_module_path(), v_module_name)
        return vmp


def bin_num(n, n_bits):
    """
    Produce a signed representation of the number n using n_bits.

    :param n: Number n
    :param n_bits: Number of bits
    :return:
    """
    mask = (2 << n_bits - 1) - 1
    num = int(n) & mask
    f_str = '{:0' + str(n_bits) + 'b}'
    f_res = f_str.format(int(num))
    return f_res
