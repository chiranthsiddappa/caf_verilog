from caf_verilog.sig_gen import SigGen
from tempfile import TemporaryDirectory
import os
import unittest
import cocotb
from cocotb.runner import get_runner, Simulator
from pathlib import Path
import glob

class TestSigGen(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
        self.sim = os.getenv("SIM", "verilator")

    def tearDown(self) -> None:
        super().tearDown()
    
    def get_runner(self) -> Simulator:
        return get_runner(self.sim)

    def test_sig_gen_output(self):
        with TemporaryDirectory() as tmpdir:
            sig_gen = SigGen(1200, 625e3, 8, output_dir=tmpdir)
            verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
            runner = self.get_runner()
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