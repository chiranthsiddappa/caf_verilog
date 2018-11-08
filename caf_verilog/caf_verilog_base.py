class CafVerilogBase:

    def gen_tb(self):
        raise NotImplementedError("This class has not implemented a testbench")

    def template_dict(self):
        raise NotImplementedError("This class has not implemented a template dictionary")

    def cpx_input_length_check(self):
        if not (len(self.x) == len(self.y)):
            raise ValueError("x and y are not the same length")