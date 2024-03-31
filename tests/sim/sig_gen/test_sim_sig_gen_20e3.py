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
async def gen_signal_20e3_via_sim(dut):
    f_clk = 625e3
    f_out = 20e3
    n_bits = 8
    num_phase_bits = calc_smallest_phase_size(f_clk, 10, n_bits)
    increment = phase_increment(f_out=f_out, phase_bits=num_phase_bits, f_clk=f_clk)
    output_file = open('sig_gen_output_%d.txt' % f_out, mode='+w')
    clock = Clock(dut.clk, 10, units="ns")  # Create a 10ns period clock on port clk

    dut.freq_step.value = increment
    dut.m_axis_data_tready.value = 0
    dut.m_axis_freq_step_tvalid.value = 0
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    for _ in range(5):
        await RisingEdge(dut.clk)

    dut.m_axis_freq_step_tvalid.value = 1

    for _ in range(0, 5):
        await RisingEdge(dut.clk)

    dut.m_axis_freq_step_tvalid.value = 1

    # Setup test values
    i_vals = np.arange(0, 512*200)
    cosine_validate = np.cos(2 * np.pi * (f_out / f_clk) * i_vals)
    sin_validate = np.sin(2 * np.pi * (f_out / f_clk) * i_vals)
    cosine_validate_q = quantize(cosine_validate, n_bits)
    sin_validate_q = quantize(sin_validate, n_bits)

    cosine_generated_values = []
    sine_generated_values = []
    output_df = pd.DataFrame()

    dut.m_axis_data_tready.value = 1
    
    for i in i_vals:
        await RisingEdge(dut.clk)
        assert dut.s_axis_data_tvalid.value == 1
        if i == 0:  # Make sure we start at cos 1, sine 0
            assert dut.cosine.value == 127  # 8 bits signed
            assert dut.sine.value == 0
        cosine_generated_values.append(int(dut.cosine.value.signed_integer))
        sine_generated_values.append(int(dut.sine.value.signed_integer))
    
    output_df['cosine_out'] = cosine_generated_values
    output_df['sine_out'] = sine_generated_values
    output_df['cosine_q'] = cosine_validate_q
    output_df['sine_q'] = sin_validate_q
    output_df['cosine_validate'] = cosine_validate
    output_df['cosine_validate'] = sin_validate
    output_df.to_csv(output_file)

    # Verify Cosine signal location
    Px_gen, f_gen = my_psd(cosine_generated_values, 2**12, f_clk)
    Px_q, f_q = my_psd(cosine_validate_q, 2**12, f_clk)
    assert np.argmax(Px_gen) == np.argmax(Px_q)
    #Verify Sine signal location
    Px_gen, f_gen = my_psd(sine_generated_values, 2**12, f_clk)
    Px_q, f_q = my_psd(sin_validate_q, 2**12, f_clk)
    assert np.argmax(Px_gen) == np.argmax(Px_q)

    assert cosine_generated_values[0] != cosine_generated_values[1]
    assert sine_generated_values[0] != sine_generated_values[1]

def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    sig_gen = SigGen(10, 625e3, 8)
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
        build_args=["--threads", str(get_sim_cpus())]
    )
    runner.test(hdl_toplevel="%s" % sig_gen.sig_gen_name, test_module="test_sim_sig_gen_20e3,")

if __name__ == '__main__':
    test_via_cocotb()