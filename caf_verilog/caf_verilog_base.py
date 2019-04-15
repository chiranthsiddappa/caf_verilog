import inflection
import os
from jinja2 import Environment, FileSystemLoader


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

    def write_module(self):
        t_dict = self.template_dict()
        template_loader = FileSystemLoader(searchpath=self.tb_module_path())
        env = Environment(loader=template_loader)
        template = env.get_template(self.module_name() + '.v')
        module_inst = template.render(**t_dict)
        with open(os.path.join(self.output_dir, self.module_name() + '.v'), 'w+') as module_file:
            module_file.write(module_inst)
