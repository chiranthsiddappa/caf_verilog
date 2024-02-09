from caf_verilog.caf_slice import CAFSlice
import os
import pathlib
import unittest
from caf_verilog.sim_helper import sim_get_runner
import glob
import numpy as np


class TestBuildCAFSlice(unittest.TestCase):

    def test_build_caf_slice(self):
        x = np.ones(100)
        y = np.ones(100)
        f_size = 24
        foas = np.arange(-f_size, f_size + 1) * 1000
        output_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'caf_slice_v')
        pathlib.Path(output_dir).mkdir(exist_ok=True)
        caf_slice = CAFSlice(x, y, foas, output_dir=output_dir)
        verilog_sources = [os.path.join(output_dir, filename) for filename in glob.glob("%s/*.v" % output_dir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % caf_slice.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=caf_slice.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True
        )


if __name__ == '__main__':
    unittest.main()
