from caf_verilog.dot_prod_pip import DotProdPip
from tempfile import TemporaryDirectory
import os
import unittest
from caf_verilog.sim_helper import sim_get_runner
import glob
import numpy as np

class TestBuildDotProdPip(unittest.TestCase):

    def test_build_dot_prod_pip(self):
        x = np.zeros(100)
        y = np.zeros(100)
        with TemporaryDirectory() as tmpdir:
            dot_prod_pip = DotProdPip(x, y, output_dir=tmpdir)
            verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
            runner = sim_get_runner()
            hdl_toplevel = "%s" % dot_prod_pip.module_name()
            runner.build(
                verilog_sources=verilog_sources,
                parameters=dot_prod_pip.params_dict(),
                vhdl_sources=[],
                hdl_toplevel=hdl_toplevel,
                always=True
            )

if __name__ == '__main__':
    unittest.main()