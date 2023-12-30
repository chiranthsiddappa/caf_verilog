from caf_verilog.dot_prod_pip import DotProdPip, send_test_input_data, capture_test_output_data
from caf_verilog.quantizer import quantize
from caf_verilog.sim_helper import sim_get_runner

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import glob
from tempfile import TemporaryDirectory
from gps_helper.prn import PRN
import numpy as np
from numpy import testing as npt


@cocotb.test()
async def verify_cpx_calcs(dut):
    fs = 1
    vals = 10000
    dot_length = 1000
    expected_outputs = vals / dot_length
    n = np.arange(0, vals)
    x = np.exp(2 * np.pi * 0.15 * n * 1j)
    y = np.exp(-2 * np.pi * 0.05 * n * 1j)
    x_quant = quantize(x, 12)
    y_quant = quantize(y, 12)
    zipped_input_values = list(zip(x_quant, y_quant))
    cpx_became_valid = False
    prod_became_valid = False
    max_length_counter = -1

    cpx_output_i = []
    cpx_output_q = []

    assert len([np.dot(x_quant[:1000], y_quant[:1000])]) == 1

    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))

    await RisingEdge(dut.clk)
    dut.m_axis_product_tready.value = 0
    dut.m_axis_x_tvalid.value = 0
    dut.m_axis_y_tvalid.value = 0
    assert dut.s_axis_product_tvalid.value == 0
    assert dut.length_counter.value.signed_integer == -1
    prev_length_counter = -1
    assert dut.length_counter_extended.value.signed_integer == -1

    while len(zipped_input_values) or len(output_cap) < expected_outputs:
        await RisingEdge(dut.clk)
        assert int(dut.length_counter.value.signed_integer) == int(dut.length_counter_extended.value.signed_integer)
        cpx_became_valid |= dut.s_axis_cpx_tvalid.value == 1
        if dut.s_axis_cpx_tvalid.value == 1:
            cpx_output_i.append(dut.mult_out_i.value.signed_integer)
            cpx_output_q.append(dut.mult_out_q.value.signed_integer)
        prod_became_valid |= dut.s_axis_product_tvalid.value == 1
        max_length_counter = max(max_length_counter, dut.length_counter.value.signed_integer)
        if len(zipped_input_values):
            x_uz, y_uz = zipped_input_values.pop(0)
            await send_test_input_data(dut, x_uz, y_uz)
        if len(output_cap) < expected_outputs:
            output_val = await capture_test_output_data(dut)
            if output_val:
                output_cap.append(output_val)
        else:
            dut.m_axis_product_tready.value = 0

    await RisingEdge(dut.clk)
    dut.m_axis_x_tvalid.value = 0
    dut.m_axis_y_tvalid.value = 0
    dut.m_axis_product_tready.value = 0

    assert cpx_became_valid
    assert max_length_counter == 999
    assert prod_became_valid
    assert len(output_cap) == expected_outputs

    # Validate all the cpx multiply outputs from within the module
    inner_cpx_output = [i + q * 1j for i, q in zip(cpx_output_i[:vals], cpx_output_q[:vals])]
    verification_cpx = x_quant * y_quant
    npt.assert_equal(verification_cpx, inner_cpx_output)

    # Validate the dot product results
    expected_dot_results = []
    for i in range(0, int(expected_outputs)):
        start_index = i * dot_length
        end_index = (i + 1) * dot_length - 1
        expected_dot = np.dot(x[start_index:end_index], y[start_index:end_index])
        expected_dot_results.append(expected_dot)
    expected_dot_results = quantize(expected_dot_results, 24)
    #npt.assert_equal(expected_dot_results, output_cap)
    


def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    with TemporaryDirectory() as tmpdir:
        x_vals = np.zeros(1000)
        y_vals = np.zeros(1000)
        dot_prod_pip = DotProdPip(x_vals, y_vals, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % dot_prod_pip.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=dot_prod_pip.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True,
            build_args=["--trace", "--trace-structs"]
        )
        runner.test(hdl_toplevel="%s" % dot_prod_pip.module_name(), test_module='test_dot_product_sin')

if __name__ == '__main__':
    test_via_cocotb()
