import pathlib

from caf_verilog.caf_slice import CAFSlice, send_and_receive, gen_tb_values
from caf_verilog.sig_gen import calc_smallest_phase_size, phase_increment
from tempfile import TemporaryDirectory
import glob
import os

from caf_verilog.sim_helper import sim_get_runner, sim_shift, get_sim_cpus
from caf_verilog.quantizer import quantize
import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from sk_dsp_comm import sigsys as ss
from gps_helper.prn import PRN

fs = 625e3
f_shift = 20e3
freq_res = 10
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
async def verify_caf_slice_time_shifts(dut):
    status_file = open(os.path.join(output_dir, "status_file.txt"), 'w', buffering=1)
    # Step related calcs
    num_phase_bits = calc_smallest_phase_size(fs, freq_res, n_bits)
    # assert num_phase_bits == 12
    increment = phase_increment(f_out=f_shift, phase_bits=num_phase_bits, f_clk=fs)

    clock = Clock(dut.clk, period=10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))

    await RisingEdge(dut.clk)
    assert dut.s_axis_tready.value == 0

    await RisingEdge(dut.clk)
    dut.freq_step.value = increment
    dut.freq_step_valid.value = 1
    dut.neg_shift.value = 1

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.s_axis_tready.value == 1

    for _ in range(0, 10):
        await RisingEdge(dut.clk)

    for shift_in_range in range(-1 * shift_range, shift_range + 1, 5):
        status_file.write("Starting Time Shift: %d\n" % shift_in_range)
        ref_quant, rec_quant = generate_test_signals(time_shift=shift_in_range, freq_shift=f_shift, f_samp=fs)
        assert len(ref_quant) == corr_length
        assert len(rec_quant) == corr_length * 2
        ref_quant_tb, rec_quant_tb = gen_tb_values(ref_quant, rec_quant)
        input_val_pairs = list(zip(ref_quant_tb, rec_quant_tb))

        assert (len(input_val_pairs) % len(ref_quant)) == 0
        assert len(input_val_pairs) == (len(ref_quant) ** 2 + len(ref_quant))
        output_cap = await send_and_receive(dut, ref_quant_tb, rec_quant_tb)

        index_to_verify = output_cap[0][1]
        out_max = output_cap[0][0].value
        assert index_to_verify.value == half_length - shift_in_range
        status_file.write("Completed Time Shift: %d index: %d out_max %d\n" % (shift_in_range,
                          int(index_to_verify.value), int(out_max)))

        for _ in range(0, 10):
            await RisingEdge(dut.clk)

    for _ in range(0, 100):
        await RisingEdge(dut.clk)


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
        runner.test(hdl_toplevel=hdl_toplevel, test_module='test_caf_slice_time_shifts')
