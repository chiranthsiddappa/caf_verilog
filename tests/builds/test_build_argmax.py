from caf_verilog.arg_max import ArgMax
from tempfile import TemporaryDirectory
import os
import unittest
from caf_verilog.sim_helper import sim_get_runner
import glob
import numpy as np

class TestArgMaxGen(unittest.TestCase):

    def test_build_arg_max(self):
        with TemporaryDirectory() as tmpdir:
            x_rand = np.random.rand(100)
            arg_max = ArgMax(x_rand, output_dir=tmpdir)
            verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
            assert len(verilog_sources) > 0
            runner = sim_get_runner()
            hdl_toplevel = "%s" % arg_max.module_name()
            runner.build(
                verilog_sources=verilog_sources,
                parameters=arg_max.params_dict(),
                vhdl_sources=[],
                hdl_toplevel=hdl_toplevel,
                always=True
            )

if __name__ == '__main__':
    unittest.main()