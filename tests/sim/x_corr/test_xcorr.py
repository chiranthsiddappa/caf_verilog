from caf_verilog.xcorr import XCorr, capture_test_output_data, send_test_input_data, gen_tb_values
from tempfile import TemporaryDirectory
import os
import pathlib
from caf_verilog.sim_helper import sim_get_runner, sim_shift
from caf_verilog.quantizer import quantize
import glob
import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from sk_dsp_comm import sigsys as ss
from gps_helper.prn import PRN

center = 300
corr_length = 250
shift = 25

def generate_test_signals():
    prn = PRN(10)
    prn2 = PRN(20)
    fs = 625e3
    Ns = fs / 125e3
    prn_seq = prn.prn_seq()
    prn_seq2 = prn2.prn_seq()
    prn_seq,b = ss.nrz_bits2(np.array(prn_seq), Ns)
    prn_seq2,b2 = ss.nrz_bits2(np.array(prn_seq2), Ns)
    ref, rec = sim_shift(prn_seq, center, corr_length, shift=shift)
    ref_quant = quantize(ref, 12)
    rec_quant = quantize(rec, 12)
    return ref_quant, rec_quant


@cocotb.test()
async def verify_xcorr_via_prn(dut):
    ref_quant, rec_quant = generate_test_signals()
    ref_quant, rec_quant = gen_tb_values(ref_quant, rec_quant)
    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tvalid.value = 0
    dut.m_axis_tready.value = 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tready.value == 0
    assert dut.s_axis_tvalid.value == 0

    for ref_cpx_val, rec_cpx_val in zip(ref_quant, rec_quant):
        await RisingEdge(dut.clk)
        dut.m_axis_tready.value = 1
        await send_test_input_data(dut, ref_cpx_val, rec_cpx_val)
        output_max, captured_index = await capture_test_output_data(dut)
        if output_max and captured_index:
            output_cap.append((output_max, captured_index))

    dut.m_axis_tvalid.value = 0

    while (not output_cap):
        await RisingEdge(dut.clk)
        output_max, captured_index = await capture_test_output_data(dut)
        if output_max and captured_index:
            output_cap.append((output_max, captured_index))
    
    index_to_verify = output_cap[0][1]
    assert index_to_verify == (corr_length / 2) - shift

    await RisingEdge(dut.clk)
    dut.m_axis_tready.value = 0

    for _ in range(0, 5):
        await RisingEdge(dut.clk)


def test_via_cocotb():
    with TemporaryDirectory() as tmpdir:
        ref_quant, rec_quant = generate_test_signals()
        x_corr = XCorr(ref=ref_quant, rec=rec_quant, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % x_corr.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=x_corr.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True,
            build_args=["--trace", "--trace-structs"]
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module="test_xcorr")


if __name__ == '__main__':
    test_via_cocotb()
