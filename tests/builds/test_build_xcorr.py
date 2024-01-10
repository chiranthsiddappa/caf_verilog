from caf_verilog.xcorr import XCorr
from tempfile import TemporaryDirectory
import os
import pathlib
import unittest
from caf_verilog.sim_helper import sim_get_runner
import glob
import numpy as np

class TestBuildXCorr(unittest.TestCase):

    def test_build_xcorr(self):
        x = np.zeros(100)
        y = np.zeros(100)
        output_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'xcorr_v')
        pathlib.Path(output_dir).mkdir(exist_ok=True)
        xcorr = XCorr(x, y, output_dir=output_dir)
        verilog_sources = [os.path.join(output_dir, filename) for filename in glob.glob("%s/*.v" % output_dir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % xcorr.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=xcorr.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True
        )

if __name__ == '__main__':
    unittest.main()