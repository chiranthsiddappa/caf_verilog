from caf_verilog.freq_shift import FreqShift, send_test_input_data, capture_test_output_data
from caf_verilog.sig_gen import calc_smallest_phase_size, phase_increment
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
from sk_dsp_comm.digitalcom import my_psd

fs = 625e3
freq_res = 200
n_bits = 8
n = np.arange(0,10e3)
f_out = 50e3
x = np.exp(2*np.pi*((f_out)/fs)*n*1j)

@cocotb.test()
async def verify_freq_shift(dut):
    clock = Clock(dut.clk, 10, units='ns')
    output_cap = []
    vals = len(n)
    x_quant = quantize(x, 12)
    x_val_iter = 0

    # Setup test values
    cosine_validate = x.real
    cosine_validate_q = np.array(quantize(cosine_validate, n_bits=n_bits))

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tready.value = 0
    dut.m_axis_tvalid.value = 0
    dut.neg_shift.value = 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tvalid == 0
    assert dut.s_axis_tready == 0

    assert RisingEdge(dut.clk)
    dut.freq_step.value = 0
    dut.freq_step_valid.value = 1

    while (dut.s_axis_tready.value == 0):
        await RisingEdge(dut.clk)
        assert dut.s_axis_mult_tready.value == 1

    # Send and capture data
    while (x_val_iter < vals or len(output_cap) < vals): # TODO: Output Capture length should match
        await RisingEdge(dut.clk)
        if x_val_iter < vals:
            next_input_vals = x_quant[x_val_iter]
            await send_test_input_data(dut, next_input_vals)
            x_val_iter += 1
        else:
            dut.m_axis_tvalid.value = 0
        if len(output_cap) < vals:
            last_capture = await capture_test_output_data(dut)
            if last_capture:
                output_cap.append(last_capture)
        else:
            dut.m_axis_tready.value = 0

    for _ in range(0, 10):
        await RisingEdge(dut.clk)
    assert dut.s_axis_tvalid.value == 0
    assert dut.s_axis_tready.value == 1

    assert len(output_cap) == vals
    npt.assert_equal(output_cap[0].real, 1015)

    # Verify that cosine has not been shifted in frequency
    Px_gen, f_gen = my_psd(cosine_validate_q, 2**12, fs)
    Px_q, f_q = my_psd(np.array(output_cap).real, 2**12, fs)
    assert np.argmax(Px_gen) == np.argmax(Px_q)


def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    with TemporaryDirectory() as tmpdir:
        fq = FreqShift(x, freq_res, fs, n_bits, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % fq.freq_shift_name
        template_dict_all = fq.template_dict()
        assert template_dict_all['freq_shift_phase_bits'] == fq.phase_bits
        assert fq.params_dict()['phase_bits'] == fq.phase_bits
        assert template_dict_all['phase_bits'] == fq.phase_bits
        # Verify expected input values by magnitude
        fq_xr_max, fq_xr_min, fq_xi_max, fq_xi_min = max(fq.x_quant.real), min(fq.x_quant.real), max(fq.x_quant.imag), min(fq.x_quant.imag)
        assert fq_xr_max == 2047
        assert fq_xr_min == -2031
        assert fq_xi_max == 2043
        assert fq_xi_min == -2043
        runner.build(
            verilog_sources=verilog_sources,
            parameters = fq.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=False,
            build_args=["--threads", str(get_sim_cpus())]
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module='test_freq_shift_no_step', waves=True)

if __name__ == '__main__':
    test_via_cocotb()
