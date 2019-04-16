import os
import csv
from . quantizer import bin_num


def write_quantized_output(output_dir, filename, x, y=None):
    """
    Write an output file with x.real,x.imag,y.real,y.imag values into a comma delimited file.

    :param output_dir:
    :param filename:
    :param x:
    :param y:
    :return:
    """
    y_vals = type(y) is not type(None)
    with open(os.path.join(output_dir, filename), 'w+') as quant_file:
        quant_writer = csv.writer(quant_file, delimiter=',')
        for ii in range(0, len(x)):
            row = [int(x[ii].real), int(x[ii].imag)]
            if y_vals:
                row.append(int(y[ii].real))
                row.append(int(y[ii].imag))
            quant_writer.writerow(row)


def write_buffer_values(output_dir, buffer_filename, buffer_quant, i_bits=12, q_bits=None):
    """

    :param output_dir:
    :param buffer_filename:
    :param buffer_quant:
    :param i_bits:
    :param q_bits:
    :return:
    """
    q_bits = i_bits if not q_bits else q_bits
    with open(os.path.join(output_dir, buffer_filename), 'w+') as rbf:
        for val in buffer_quant:
            i_bin = bin_num(val.real, i_bits)
            q_bin = bin_num(val.imag, q_bits)
            rbf.write(i_bin + q_bin + "\n")


def read_complex_output(filename):
    """
    Read a file written with complex output, ex. i,j

    :param filename: Full path to open a file handler with.
    :return:
    """
    cpx = []
    with open(filename) as cpx_file:
        cpx_reader = csv.reader(cpx_file, delimiter=',')
        for row in cpx_reader:
            try:
                i_data = int(row[0])
                q_data = int(row[1]) * 1j
                cpx.append(i_data + q_data)
            except TypeError as te:
                Warning(te)
            except ValueError as ve:
                Warning(ve)
            except IndexError as ie:
                Warning(ie)
    return cpx
