import os
import csv


def write_quantized_output(output_dir, filename, x, y):
    """
    Write an output file with x.real,x.imag,y.real,y.imag values into a comma delimited file.

    :param output_dir:
    :param filename:
    :param x:
    :param y:
    :return:
    """
    with open(os.path.join(output_dir, filename), 'w+') as quant_file:
        quant_writer = csv.writer(quant_file, delimiter=',')
        for ii in range(0, len(x)):
            row = [x[ii].real, x[ii].imag, y[ii].real, y[ii].imag]
            quant_writer.writerow(row)
