from caf_verilog.sig_gen import SigGen, calc_smallest_phase_size, phase_increment
from caf_verilog.quantizer import quantize
import os
import cocotb
from cocotb.clock import Clock
from caf_verilog.sim_helper import sim_get_runner, get_sim_cpus
from cocotb.triggers import RisingEdge
import glob
import numpy as np
import pandas as pd
from sk_dsp_comm.digitalcom import my_psd


@cocotb.test()
async def gen_signal_fs_4_via_sim(dut):
    f_clk = 625e3
    f_out = f_clk / 4
    n_bits = 8
    num_phase_bits = calc_smallest_phase_size(f_clk, 1200, n_bits)
    increment = phase_increment(f_out=f_out, phase_bits=num_phase_bits, f_clk=f_clk)
    output_file = open('sig_gen_output_%d.txt' % f_out, mode='+w')
    clock = Clock(dut.clk, 10, units="ns")  # Create a 10ns period clock on port clk

    dut.freq_step.value = increment
    dut.m_axis_data_tready.value = 0
    dut.m_axis_freq_step_tvalid.value = 0
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    for _ in range(0, 5):
        await RisingEdge(dut.clk)

    dut.m_axis_freq_step_tvalid.value = 1

    for _ in range(0, 5):
        await RisingEdge(dut.clk)
        dut.m_axis_freq_step_tvalid.value = 0

    assert dut.s_axis_data_tvalid.value == 1
    assert dut.cosine.value == 127
    assert dut.sine.value == 0

    dut.m_axis_data_tready.value = 1

    await RisingEdge(dut.clk)
    assert dut.s_axis_data_tvalid.value == 1
    assert dut.cosine.value == 127
    assert dut.sine.value == 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_data_tvalid.value == 1
    assert dut.cosine.value != 127
    assert dut.sine.value != 0

    for _ in range(0, 5):
        await RisingEdge(dut.clk)
        dut.m_axis_data_tready.value = 0

    increment = phase_increment(f_out=f_out / 4, phase_bits=num_phase_bits, f_clk=f_clk)
    dut.freq_step.value = increment
    dut.m_axis_freq_step_tvalid.value = 1
    dut.m_axis_data_tready.value = 1

    for _ in range(0, 5):
        assert dut.s_axis_data_tvalid.value == 1
        await RisingEdge(dut.clk)
        dut.m_axis_freq_step_tvalid.value = 0


def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    sig_gen = SigGen(1200, 625e3, 8)
    verilog_sources = [os.path.join('.', filename) for filename in glob.glob("%s/*.v" % '.')]
    sig_gen.gen_tb()
    runner = sim_get_runner()
    hdl_toplevel = "%s" % sig_gen.sig_gen_name
    runner.build(
        verilog_sources=verilog_sources,
        parameters=sig_gen.params_dict(),
        vhdl_sources=[],
        hdl_toplevel=hdl_toplevel,
        always=False,
        build_args=["--trace", "--trace-structs", "--threads", str(get_sim_cpus())]
    )
    runner.test(hdl_toplevel="%s" % sig_gen.sig_gen_name,
                test_module="test_sim_sig_gen_turnarounds,", waves=True)

if __name__ == '__main__':
    test_via_cocotb()