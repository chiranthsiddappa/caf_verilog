from caf_verilog.arg_max import ArgMax
from caf_verilog.quantizer import quantize
from tempfile import TemporaryDirectory
import os
import unittest
from caf_verilog.sim_helper import sim_get_runner
import glob
import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

import numpy as np
from numpy import testing as npt


@cocotb.test()
async def verify_arg_max(dut):
    i_random = np.arange(2048)
    q_random = np.arange(2048)
    x_vals = i_random + q_random*-1j
    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tready.value = 0
    dut.m_axis_tvalid.value = 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tready.value == 0
    assert dut.s_axis_tvalid.value == 0

    # Send and capture data
    for x_val in x_vals:
        await RisingEdge(dut.clk)
        assert dut.s_axis_tready.value == 1
        dut.m_axis_tvalid.value = 1
        dut.xi.value = int(x_val.real)
        dut.xq.value = int(x_val.imag)

    while (dut.s_axis_tvalid.value == 0):
        await RisingEdge(dut.clk)
        dut.m_axis_tready.value = 1
        dut.m_axis_tvalid.value = 0

    assert dut.s_axis_tvalid.value == 1
    assert dut.index == 2047

    for _ in range(0, 5):
        dut.m_axis_tready.value = 0
        await RisingEdge(dut.clk)
            
    

def test_via_cocotb():
    with TemporaryDirectory() as tmpdir:
        x_rand = np.random.rand(2048)
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
            always=True,
            build_args=["--trace", "--trace-structs"]
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module="test_argmax_linspace")

if __name__ == '__main__':
    test_via_cocotb()
