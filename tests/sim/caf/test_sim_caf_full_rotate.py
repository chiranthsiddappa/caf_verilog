import glob
import os
import pathlib

from caf_verilog.sim_helper import sim_get_runner, sim_shift, get_sim_cpus
from caf_verilog.quantizer import quantize
from caf_verilog.caf import CAF, set_increment_values, send_input_data, retrieve_max

import numpy as np
import unittest
import pytest
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from sk_dsp_comm import sigsys as ss
from gps_helper.prn import PRN

__rotate_mode__ = os.getenv("CAF_ROTATE", "small")

fs = 625e3
f_shift = 20e3
n_bits = 12
center = 450
corr_length = 250
default_shift = 0
half_length = corr_length / 2
shift_range = int(half_length)
f_size = 100
foas = np.arange(-f_size, f_size + 1) * 1000

output_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'caf_v_full_rotate')
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
    ref_quant = quantize(ref, n_bits=n_bits)
    rec_quant = quantize(rec, n_bits=n_bits)
    return ref_quant, rec_quant


ref_quant, rec_quant = generate_test_signals(time_shift=default_shift, freq_shift=f_shift, f_samp=fs)
caf = CAF(ref_quant, rec_quant, foas=foas, n_bits=n_bits, ref_i_bits=12, rec_i_bits=12, output_dir=output_dir)


@cocotb.test()
async def caf_verify_all_peaks(dut):
    status_file = open(os.path.join(output_dir, "caf_full_rotate_status_file.csv"), 'w', buffering=1)

    clock = Clock(dut.clk, period=10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))

    for _ in range(0, 5):
        await RisingEdge(dut.clk)

    await set_increment_values(caf, dut)

    status_file.write("time_index,time_index_expected,foa,foa_expected,out_max\n")
    for idf, freq_shift_v in enumerate(foas):
        for shift_in_range in range(-1 * shift_range, shift_range + 1, 5):
            ref_quant_v, rec_quant_v = generate_test_signals(time_shift=shift_in_range,
                                                             freq_shift=freq_shift_v,
                                                             f_samp=fs)
            caf.ref_quant = ref_quant_v
            caf.rec_quant = rec_quant_v

            await send_input_data(caf, dut)

            time_index, foa_value, out_max = await retrieve_max(caf, dut)
            time_loc_verify = half_length - shift_in_range
            time_index_correct = time_index == time_loc_verify
            foa_correct = foa_value == freq_shift_v
            status_file.write("%d,%d,%d,%d,%d\n" % (time_index, time_loc_verify,
                                                    foa_value, freq_shift_v,
                                                    out_max))

            assert time_index_correct
            assert foa_correct

    for _ in range(5):
        await RisingEdge(dut.clk)


@pytest.mark.skipif(__rotate_mode__.lower() != "full", reason="CAF Rotate mode is %s" % __rotate_mode__)
def test_via_cocotb():
    verilog_sources = [os.path.join(output_dir, filename) for filename in glob.glob("%s/*.v" % output_dir)]
    runner = sim_get_runner()
    hdl_toplevel = "%s" % caf.module_name()
    caf_params = caf.params_dict()
    runner.build(
        verilog_sources=verilog_sources,
        parameters=caf_params,
        vhdl_sources=[],
        hdl_toplevel=hdl_toplevel,
        always=True,
        build_args=["--threads", str(get_sim_cpus())]
    )
    runner.test(hdl_toplevel=hdl_toplevel, test_module='test_sim_caf_full_rotate', waves=True)


if __name__ == '__main__':
    unittest.main()
