from sk_dsp_comm.sigsys import simpleQuant
import numpy as np


def quantize(data, n_bits, n_bits_imag=0):
    """
    Quantize the data into a range from -X to X within the n_bits size limit.

    :param data:
    :param n_bits:
    :param n_bits_imag:
    :return:
    """
    cpx_check = is_complex(data)
    if not cpx_check:
        x_max = get_max(data)
        q_data = simpleQuant(data, n_bits, x_max, 'sat')
        q_data = scale(q_data, n_bits, x_max)
        return q_data
    else:
        cpx_data = np.array(data)
        cpx_data_real = cpx_data.real
        cpx_data_imag = cpx_data.imag
        x_max_real = get_max(cpx_data_real)
        x_max_imag = get_max(cpx_data_imag)
        q_data_real = simpleQuant(cpx_data_real, n_bits, x_max_real, 'sat')
        if not n_bits_imag:
            n_bits_imag = n_bits
        q_data_imag = simpleQuant(cpx_data_imag, n_bits_imag, x_max_imag, 'sat')
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


def scale(data, n_bits, x_max):
    """
    Takes values and scales them to the max of the n_bits limit.

    :param data:
    :param n_bits:
    :param x_max:
    :return:
    """
    return data * (2**n_bits) / x_max


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
