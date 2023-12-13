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


async def capture_test_output_data(dut, num_expected_values) -> list:
    captured_values = []
    captured_output_file = 'cpx_multiply_output.csv'
    captured_output_file = open(captured_output_file, mode='+w')
    captured_output_file.write('captured_output\n')
    dut.m_axis_tready.value = 1
    for _ in range(0, num_expected_values):
        while(dut.s_axis_tvalid == 0):
            await RisingEdge(dut.clk)
        if dut.s_axis_tvalid == 1:
            captured_i = dut.i.value.signed_integer
            captured_q = dut.q.value.signed_integer
            last_complex = captured_i + captured_q*1j
            captured_values.append(last_complex)
            captured_output_file.write("%s\n" % last_complex)
    dut.m_axis_tready.value = 0
    captured_output_file.close()
    await RisingEdge(dut.clk)
    return captured_values


async def send_test_input_data(dut, x, y):

    while(dut.s_axis_tready.value == 0):
        await RisingEdge(dut.clk)
    
    for x_val, y_val in zip(x, y):
        x_i = x_val.real
        x_q = x_val.imag
        y_i = y_val.real
        y_q = y_val.imag
        await RisingEdge(dut.clk)
        dut.m_axis_tvalid.value = 1
        dut.xi.value = int(x_i)
        dut.xq.value = int(x_q)
        dut.yi.value = int(y_i)
        dut.yq.value = int(y_q)
    await RisingEdge(dut.clk)
    dut.m_axis_tvalid.value = 0

@cocotb.test()
async def verify_cpx_calcs(dut):
    fs = 1
    vals = 10000
    n = np.arange(0, vals)
    x = np.exp(2 * np.pi * 0.15 * n * 1j)
    y = np.exp(-2 * np.pi * 0.05 * n * 1j)
    x_quant = quantize(x, 12)
    y_quant = quantize(y, 12)
    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tready.value = 0
    dut.m_axis_tvalid.value = 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tvalid.value == 0
    assert dut.s_axis_tready.value == 0

    cocotb.start_soon(send_test_input_data(dut, x_quant, y_quant))
    cocotb.start_soon(capture_test_output_data(dut, vals))

    for _ in range(0, 2):
        await RisingEdge(dut.clk)
        assert dut.s_axis_tvalid.value == 0
        assert dut.s_axis_tready.value == 1

    for _ in range(0, vals+1000):
        await RisingEdge(dut.clk)

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