import pathlib
import os
import glob
from tempfile import TemporaryDirectory

from caf_verilog.caf_slice import CAFSlice, send_and_receive, gen_tb_values
from caf_verilog.sig_gen import calc_smallest_phase_size, phase_increment
from caf_verilog.sim_helper import sim_get_runner, sim_shift, get_sim_cpus
from caf_verilog.quantizer import quantize

from sk_dsp_comm import sigsys as ss
from gps_helper.prn import PRN
import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

fs = 625e3
f_shift = 20e3
freq_res = 0.01
n_bits = 8
center = 450
corr_length = 250
default_shift = 0
half_length = corr_length / 2
shift_range = int(half_length)

output_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'caf_slice_v')
pathlib.Path(output_dir).mkdir(exist_ok=True)


def generate_test_signals(time_shift, freq_shift, f_samp):
    prn = PRN(10)
    fs = f_samp
    Ns = 5
    prn_seq = prn.prn_seq()
    prn_seq, b = ss.nrz_bits2(np.array(prn_seq), Ns)
    prn_seq = [*prn_seq, *prn_seq]
    prn_seq = np.array(prn_seq)
    prn_seq = prn_seq + prn_seq * 1j
    ref, rec = sim_shift(prn_seq, center, corr_length, shift=time_shift, freq_shift=freq_shift, fs=fs)
    ref_quant = quantize(ref, 12)
    rec_quant = quantize(rec, 12)
    return ref_quant, rec_quant


@cocotb.test()
async def verif_caf_slice_frequency_shifts(dut):
    status_file = open(os.path.join(output_dir, "freq_match_status_file.csv"), 'w', buffering=1)

    num_phase_bits = calc_smallest_phase_size(fs, freq_res, n_bits)

    clock = Clock(dut.clk, period=10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))

    for _ in range(10):
        await RisingEdge(dut.clk)
        assert dut.s_axis_tready.value == 0

    """
    In order to achieve a valid/runtime state, an increment of 0 will be set, and generated signals with no shift will
    be used to start the simulation.
    """
    await RisingEdge(dut.clk)
    dut.freq_step.value = 0
    dut.freq_step_valid.value = 1
    dut.neg_shift.value = 0

    while dut.s_axis_tready.value == 0:
        await RisingEdge(dut.clk)

    ref_quant, rec_quant = generate_test_signals(time_shift=default_shift, freq_shift=0, f_samp=fs)
    ref_quant_tb, rec_quant_tb = gen_tb_values(ref_quant, rec_quant)

    output_max, index = await send_and_receive(dut, ref_quant_tb, rec_quant_tb, cycle_timeout=20)

    index_to_verify = index.value
    out_max = output_max.value
    assert index_to_verify == half_length - default_shift

    status_file.write("frequency_shift,index,out_max\n")

    """
    Begin all frequencies, including zero.
    """
    f_size = 100
    foas = np.arange(-f_size, f_size + 1) * 1000
    for idx, freq_shift in enumerate(foas):
        increment = phase_increment(f_out=freq_shift, phase_bits=num_phase_bits, f_clk=fs)

        dut.freq_step.value = increment
        dut.freq_step_valid.value = 1
        dut.neg_shift.value = 1 if (freq_shift < 0) else 0

        ref_quant, rec_quant = generate_test_signals(time_shift=default_shift, freq_shift=freq_shift, f_samp=fs)
        ref_quant_tb, rec_quant_tb = gen_tb_values(ref_quant, rec_quant)
        output_max, index = await send_and_receive(dut, ref_quant_tb, rec_quant_tb, cycle_timeout=20)
        index_to_verify = index.value
        out_max = output_max.value

        status_file.write("%d,%d,%d\n" % (freq_shift, int(index_to_verify), int(out_max)))
        assert index_to_verify == half_length - default_shift


def test_via_cocotb():
    with TemporaryDirectory() as tmpdir:
        ref_quant, rec_quant = generate_test_signals(time_shift=default_shift, freq_shift=f_shift, f_samp=fs)
        caf_slice = CAFSlice(ref_quant, rec_quant, freq_res=freq_res, n_bits=n_bits, fs=fs, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % caf_slice.module_name()
        cs_params = caf_slice.params_dict()
        assert 'length' in cs_params
        assert cs_params['length'] == len(ref_quant) + 2  # Plus two added by
        runner.build(
            verilog_sources=verilog_sources,
            parameters=cs_params,
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=False,
            build_args=["--threads", str(get_sim_cpus())]
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module='test_caf_slice_freq_match')
