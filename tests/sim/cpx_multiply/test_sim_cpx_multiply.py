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
from numpy import testing as npt


async def capture_test_output_data(dut):
    captured_output = dut.i.value.signed_integer + dut.q.value.signed_integer * 1j
    dut.m_axis_tready.value = 1
    if dut.s_axis_tvalid.value == 1:
        return captured_output
    else:
        return None


async def send_test_input_data(dut, x, y):
    
    assert dut.s_axis_tready.value == 1 # Just to double check
    x_i = int(x.real)
    x_q = int(x.imag)
    y_i = int(y.real)
    y_q = int(y.imag)

    dut.xi.value = int(x_i)
    dut.xq.value = int(x_q)
    dut.yi.value = int(y_i)
    dut.yq.value = int(y_q)
    dut.m_axis_tvalid.value = 1

@cocotb.test()
async def verify_cpx_calcs(dut):
    fs = 1
    vals = 10000
    n = np.arange(0, vals)
    x = np.exp(2 * np.pi * 0.15 * n * 1j)
    y = np.exp(-2 * np.pi * 0.05 * n * 1j)
    x_quant = quantize(x, 12)
    y_quant = quantize(y, 12)
    zipped_input_values = list(zip(x_quant, y_quant))
    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tready.value = 0
    dut.m_axis_tvalid.value = 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tvalid.value == 0
    assert dut.s_axis_tready.value == 0

    # Send and capture data
    while (len(zipped_input_values) or len(output_cap) < vals):
    #while( len(zipped_input_values) ):
        await RisingEdge(dut.clk)
        assert dut.s_axis_tready.value == 1
        if len(zipped_input_values):
            next_input_vals = zipped_input_values.pop(0)
            await send_test_input_data(dut, next_input_vals[0], next_input_vals[1])
        else:
            dut.m_axis_tvalid.value = 0
        if len(output_cap) < vals:
            last_capture = await capture_test_output_data(dut)
            if last_capture:
                output_cap.append(last_capture)
        else:
            dut.m_axis_tready.value = 0

    # Verify the values are correct via numpy testing
    npt.assert_equal(x_quant * y_quant, output_cap)
    
    for _ in range(0, vals+1000):
        await RisingEdge(dut.clk)
    assert dut.s_axis_tvalid.value == 0
    assert dut.s_axis_tready.value == 1

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
        runner.test(hdl_toplevel="%s" % cpx_multiply.module_name(), test_module="test_sim_cpx_multiply")

if __name__ == '__main__':
    test_via_cocotb()