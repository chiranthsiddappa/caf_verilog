from caf_verilog.sig_gen import SigGen
from tempfile import TemporaryDirectory
import os
import unittest
from caf_verilog.sim_helper import sim_get_runner
import glob

class TestSigGen(unittest.TestCase):

    def test_build_sig_gen(self):
        with TemporaryDirectory() as tmpdir:
            sig_gen = SigGen(1200, 625e3, 8, output_dir=tmpdir)
            verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
            runner = sim_get_runner()
            hdl_toplevel = "%s" % sig_gen.sig_gen_name
            runner.build(
                verilog_sources=verilog_sources,
                parameters=sig_gen.params_dict(),
                vhdl_sources=[],
                hdl_toplevel=hdl_toplevel,
                always=True,
            )



if __name__ == '__main__':
    unittest.main()