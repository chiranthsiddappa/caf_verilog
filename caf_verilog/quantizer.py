from sk_dsp_comm.sigsys import simple_quant
import numpy as np


def quantize(data, n_bits, n_bits_imag=0):
    """
    Quantize the data into a range from -X to X within the n_bits size limit.

    :param data: Data list to quantize
    :param n_bits: Real bits
    :param n_bits_imag: Imaginary bits
    :return:
    """
    cpx_check = is_complex(data)
    n_bits_1 = n_bits + 1
    if not cpx_check:
        x_max = get_max(data)
        q_data = simple_quant(data, n_bits_1, x_max, 'sat')
        q_data = scale(q_data, n_bits, x_max)
        return q_data
    else:
        cpx_data = np.array(data)
        cpx_data_real = cpx_data.real
        cpx_data_imag = cpx_data.imag
        x_max_real = get_max(cpx_data_real)
        x_max_imag = get_max(cpx_data_imag)
        q_data_real = simple_quant(cpx_data_real, n_bits_1, x_max_real, 'sat')
        if not n_bits_imag:
            n_bits_imag = n_bits
        n_bits_imag_1 = n_bits_imag + 1
        q_data_imag = simple_quant(cpx_data_imag, n_bits_imag_1, x_max_imag, 'sat')
        q_data_real = scale(q_data_real, n_bits, x_max_real)
        q_data_imag = scale(q_data_imag, n_bits_imag, x_max_imag)
        q_data = q_data_real + q_data_imag * 1j
        return q_data


def get_max(data):
    """
    Get the maximum value of the array that can be used for the -Xmax to Xmax range.

    :param data:
    :return:
    """
    return max(np.floor(max(max(data), abs(min(data)))), 1)


def scale(data, n_bits, x_max, use_complex=False):
    """
    Takes values and scales them to the max of the n_bits limit.

    :param data:
    :param n_bits:
    :param x_max:
    :return:
    """
    scaled_output = (data * (2**(n_bits-1) - 1)) / x_max
    scaled_output = np.round(scaled_output)
    return scaled_output


def is_complex(data):
    """
    Test whether the data has a complex value in it or not.

    :param data:
    :return:
    """
    cpx_check = False
    for dd in data:
        cpx_check |= isinstance(dd, complex)
    return cpx_check


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
