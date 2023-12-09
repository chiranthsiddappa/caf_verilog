from caf_verilog.cpx_multiply import CpxMultiply
from tempfile import TemporaryDirectory
import os
import unittest
from caf_verilog.sim_helper import sim_get_runner
import glob
import numpy as np

class TestBuildCpxMultiply(unittest.TestCase):

    def test_build_cpx_multiply(self):
        x = np.zeros(100)
        y = np.zeros(100)
        with TemporaryDirectory() as tmpdir:
            cpx_multiply = CpxMultiply(x, y, output_dir=tmpdir)
            verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
            runner = sim_get_runner()
            hdl_toplevel = "%s" % cpx_multiply.module_name()
            runner.build(
                verilog_sources=verilog_sources,
                parameters={},
                vhdl_sources=[],
                hdl_toplevel=hdl_toplevel,
                always=True
            )

if __name__ == '__main__':
    unittest.main()