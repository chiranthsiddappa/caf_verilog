from caf_verilog.dot_prod_pip import DotProdPip, send_test_input_data, capture_test_output_data
from caf_verilog.quantizer import quantize
from caf_verilog.sim_helper import sim_get_runner, get_sim_cpus

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import glob
from tempfile import TemporaryDirectory
import numpy as np
from numpy import testing as npt
from sk_dsp_comm import sigsys as ss

n = 1024

def generate_test_signals(xi, xq, yi, yq, gen_len):
    inner_cpx_output = [xi + xq*1j for _ in range(0, gen_len)]
    inner_cpx_output_r = [yi + yq*1j for _ in range(0, gen_len)]
    return inner_cpx_output, inner_cpx_output_r

@cocotb.test()
async def verify_cpx_calcs(dut):
    x_inputs, y_inputs = list(), list()
    x_val_ver, y_val_ver = list(), list()
    test_vals = [-1, 0, 1]
    for xi in test_vals:
        for yi in test_vals:
            for xq in test_vals:
                for yq in test_vals:
                    if not ((xi or xq) and (yi or yq)):
                        continue
                    x_ver = xi + xq*1j
                    y_ver = yi + yq*1j
                    x_val_ver.append(x_ver)
                    y_val_ver.append(y_ver)
                    x_ones, y_ones = generate_test_signals(xi, xq, yi, yq, n)
                    x_quant = quantize(x_ones, 12)
                    y_quant = quantize(y_ones, 12)
                    x_inputs += list(x_quant)
                    y_inputs += list(y_quant)
    zipped_input_values = list(zip(x_inputs, y_inputs))
    num_expected_outputs = int(len(zipped_input_values) / n)

    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))

    await RisingEdge(dut.clk)
    dut.m_axis_product_tready.value = 0
    dut.m_axis_x_tvalid.value = 0
    dut.m_axis_y_tvalid.value = 0
    assert dut.s_axis_product_tvalid.value == 0
    assert dut.dot_length_counter.value.signed_integer == -1
    assert dut.dot_length_counter_extended.value.signed_integer == -1

    while len(zipped_input_values) or len(output_cap) < num_expected_outputs:
        await RisingEdge(dut.clk)
        if len(zipped_input_values):
            x_uz, y_uz = zipped_input_values.pop(0)
            await send_test_input_data(dut, x_uz, y_uz)
        if len(output_cap) < num_expected_outputs:
            output_val = await capture_test_output_data(dut)
            if output_val != False:
                output_cap.append(output_val)
        else:
            dut.m_axis_product_tready.value = 0

    await RisingEdge(dut.clk)
    dut.m_axis_x_tvalid.value = 0
    dut.m_axis_y_tvalid.value = 0
    dut.m_axis_product_tready.value = 0

    assert len(output_cap) == num_expected_outputs

    # Start verifying outputs
    x_val_ver_q = quantize(x_val_ver, 12)
    y_val_ver_q = quantize(y_val_ver, 12)

    for x_ver, y_ver, out_ver in zip(x_val_ver_q, y_val_ver_q, output_cap):
        exp_val = x_ver * y_ver
        exp_val *= n
        assert bin(int(out_ver.real)) in bin(int(exp_val.real))
        assert bin(int(out_ver.imag)) in bin(int(exp_val.imag))


def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    with TemporaryDirectory() as tmpdir:
        inner_sum, inner_sum_reverse = generate_test_signals(1, -1, -1, 1, n)
        dot_prod_pip = DotProdPip(inner_sum, inner_sum_reverse, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % dot_prod_pip.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=dot_prod_pip.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True,
            build_args=["--trace", "--trace-structs", "--threads", str(get_sim_cpus())]
        )
        runner.test(hdl_toplevel="%s" % dot_prod_pip.module_name(), test_module='test_dot_product_of')

if __name__ == '__main__':
    test_via_cocotb()
