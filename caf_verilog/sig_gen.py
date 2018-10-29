from . quantizer import quantize
from . io_helper import write_quantized_output


class SigGen:

    def __init__(self, f, output_dir='.'):
        self.f = f
        self.output_dir = output_dir