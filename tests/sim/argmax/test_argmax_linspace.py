from caf_verilog.arg_max import ArgMax, send_test_input_data, capture_test_output_data, empty_cycles
from caf_verilog.quantizer import quantize
from tempfile import TemporaryDirectory
import os
import unittest
from caf_verilog.sim_helper import sim_get_runner, get_sim_cpus
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
    expected_max_output_val = 2 * 2047 **2
    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tready.value = 0
    dut.m_axis_tvalid.value = 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tready.value == 0
    assert dut.s_axis_tvalid.value == 0

    # Send and receive capture data
    await send_test_input_data(dut, x_vals)

    index, captured_max = await capture_test_output_data(dut)
    assert index == 2047
    assert captured_max == expected_max_output_val

    await empty_cycles(dut)

    await send_test_input_data(dut, reversed(x_vals))

    index, captured_max = await capture_test_output_data(dut)
    assert index == 0
    assert captured_max == expected_max_output_val

    await empty_cycles(dut)            
    

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
            build_args=["--trace", "--trace-structs", "--threads", str(get_sim_cpus())]
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module="test_argmax_linspace")

if __name__ == '__main__':
    test_via_cocotb()
