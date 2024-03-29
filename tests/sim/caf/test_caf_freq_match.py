import glob
import os
import pathlib

from caf_verilog.sim_helper import sim_get_runner, sim_shift, get_sim_cpus
from caf_verilog.quantizer import quantize
from caf_verilog.caf import CAF, set_increment_values, send_input_data, retrieve_max

import numpy as np
import unittest
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from sk_dsp_comm import sigsys as ss
from gps_helper.prn import PRN


fs = 625e3
f_shift = 20e3
freq_res = 0.01
n_bits = 8
center = 450
corr_length = 250
default_shift = 0
half_length = corr_length / 2
shift_range = int(half_length)
f_size = 100
foas = np.arange(-f_size, f_size + 1) * 1000

output_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'caf_v_max')
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


ref_quant, rec_quant = generate_test_signals(time_shift=default_shift, freq_shift=f_shift, f_samp=fs)
caf = CAF(ref_quant, rec_quant, foas=foas, n_bits=n_bits, ref_i_bits=12, rec_i_bits=12, output_dir=output_dir)


@cocotb.test()
async def caf_verify_all_peaks(dut):
    status_file = open(os.path.join(output_dir, "caf_freq_match_status.csv"), 'w', buffering=1)

    clock = Clock(dut.clk, period=10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))

    for _ in range(0, 5):
        await RisingEdge(dut.clk)

    await set_increment_values(caf, dut)

    status_file.write("time_index,time_index_expected,foa_expected,foa,out_max\n")
    for idf, freq_shift_v in enumerate(foas):
        ref_quant_v, rec_quant_v = generate_test_signals(time_shift=default_shift, freq_shift=freq_shift_v, f_samp=fs)
        caf.ref_quant = ref_quant_v
        caf.rec_quant = rec_quant_v

        await send_input_data(caf, dut)

        time_index, foa_value, out_max = await retrieve_max(caf, dut)

        status_file.write("%d,%d,%d,%d,%d\n" % (time_index, default_shift, freq_shift_v, foa_value, out_max))
        assert time_index == half_length - default_shift
        assert foa_value == freq_shift_v

    for _ in range(5):
        await RisingEdge(dut.clk)


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
    runner.test(hdl_toplevel=hdl_toplevel, test_module='test_caf_freq_match', waves=True)


if __name__ == '__main__':
    unittest.main()
