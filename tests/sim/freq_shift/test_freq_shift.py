from caf_verilog.freq_shift import FreqShift
from caf_verilog.quantizer import quantize
from caf_verilog.sim_helper import sim_get_runner

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import glob
from tempfile import TemporaryDirectory

import numpy as np
from numpy import testing as npt

fs = 625e3
freq_res = 200
n_bits = 8
n = np.arange(0,10e3)
x = np.exp(2*np.pi*((50e3)/fs)*n*1j)

def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    with TemporaryDirectory() as tmpdir:
        fq = FreqShift(x, freq_res, fs, n_bits, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % fq.freq_shift_name
        template_dict_all = fq.template_dict()
        assert template_dict_all['freq_shift_phase_bits'] == fq.phase_bits
        assert fq.params_dict()['phase_bits'] == fq.phase_bits
        assert template_dict_all['phase_bits'] == fq.phase_bits
        runner.build(
            verilog_sources=verilog_sources,
            parameters = fq.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True
        )

if __name__ == '__main__':
    test_via_cocotb()
