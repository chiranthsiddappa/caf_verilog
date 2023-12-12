from caf_verilog.cpx_multiply import CpxMultiply
from caf_verilog.quantizer import quantize
from caf_verilog.sim_helper import sim_get_runner

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import glob
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import unittest


@cocotb.test()
async def verify_cpx_calcs(dut):
    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tready = 0
    dut.m_axis_tvalid = 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tvalid.value == 0
    assert dut.s_axis_tready.value == 1
    await RisingEdge(dut.s_axis_tvalid)
    for _ in range(0, 10):
        assert dut.s_axis_tready == 1
        assert dut.s_axis_tvalid == 1


def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    x = np.zeros(100)
    y = np.zeros(100)
    with TemporaryDirectory() as tmpdir:
        cpx_multiply = CpxMultiply(x, y, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % cpx_multiply.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=cpx_multiply.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True
        )

if __name__ == '__main__':
    unittest.main()