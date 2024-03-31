from caf_verilog.xcorr import XCorr, send_and_receive, gen_tb_values
from tempfile import TemporaryDirectory
import os
import pathlib
from caf_verilog.sim_helper import sim_get_runner, sim_shift, get_sim_cpus
from caf_verilog.quantizer import quantize
import glob
import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from sk_dsp_comm import sigsys as ss
from gps_helper.prn import PRN

center = 450
corr_length = 250
default_shift = 25
half_length = corr_length / 2
shift_range = int(half_length)

output_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'xcorr_v')
pathlib.Path(output_dir).mkdir(exist_ok=True)


def generate_test_signals(shift):
    prn = PRN(10)
    fs = 625e3
    Ns = fs / 125e3
    prn_seq = prn.prn_seq()
    prn_seq,b = ss.nrz_bits2(np.array(prn_seq), Ns)
    prn_seq = prn_seq + prn_seq * 1j
    ref, rec = sim_shift(prn_seq, center, corr_length, shift=shift)
    ref_quant = quantize(ref, 12)
    rec_quant = quantize(rec, 12)
    return ref_quant, rec_quant


@cocotb.test()
async def verify_xcorr_via_prn(dut):
    ref_quant, rec_quant = generate_test_signals(default_shift)
    ref_quant_tb, rec_quant_tb = gen_tb_values(ref_quant, rec_quant)
    input_val_pairs = list(zip(ref_quant_tb, rec_quant_tb))
    output_caps = []

    assert (len(input_val_pairs) % len(ref_quant)) == 0
    assert len(input_val_pairs) == (len(ref_quant)**2 + len(ref_quant))

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tvalid.value = 0
    dut.m_axis_tready.value = 0

    output_max, index = await send_and_receive(dut, ref_quant_tb, rec_quant_tb)

    index_to_verify = index.value
    assert index_to_verify == (corr_length / 2) - default_shift

    output_caps = await full_round_shift(dut)

    dut.m_axis_tready.value = 0

    for _ in range(0, 10):
        await RisingEdge(dut.clk)

    # Verify round shift
    for idx, shift_val in enumerate(range(-1 * shift_range, shift_range + 1)):
        assert output_caps[idx][1].value == half_length - shift_val


async def full_round_shift(dut):
    output_caps = []
    status_file = open(os.path.join(output_dir, "full_rotate_status.txt"), 'w', buffering=1)
    for shift_in_range in range(-1 * shift_range, shift_range + 1):
        status_file.write("Starting Time Shift: %d\n" % shift_in_range)
        ref_quant, rec_quant = generate_test_signals(shift_in_range)
        ref_quant_tb, rec_quant_tb = gen_tb_values(ref_quant, rec_quant)
        output_max, index = await send_and_receive(dut, ref_quant_tb, rec_quant_tb)

        index_to_verify = index.value
        out_max = output_max.value
        assert index_to_verify == half_length - shift_in_range
        output_caps.append((output_max, index))
        status_file.write("Completed Time Shift: %d index: %d out_max %d\n" % (shift_in_range,
                                                                               int(index_to_verify),
                                                                               int(out_max)))
    return output_caps


def test_via_cocotb():
    with TemporaryDirectory() as tmpdir:
        ref_quant, rec_quant = generate_test_signals(default_shift)
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
            build_args=["--threads", str(get_sim_cpus())]
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module="test_xcorr_full_rotate")


if __name__ == '__main__':
    test_via_cocotb()
