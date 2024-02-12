from caf_verilog.caf_slice import CAFSlice
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
f_out = 50e3
f_shift = 20e3
freq_res = 200
n_bits = 8
n = np.arange(0,10e3)
x = np.exp(2 * np.pi * (f_out / fs) * n * 1j)
x_q = quantize(x, n_bits)
x_shift_gen = np.exp(2 * np.pi * (f_shift / fs) * n * -1j)
x_shift_gen_q = quantize(x_shift_gen, n_bits)
x_shifted_exp_q = x_q * x_shift_gen_q
center = 300
corr_length = 250
default_shift = 25
half_length = corr_length / 2
shift_range = int(half_length)


def generate_test_signals(shift):
    prn = PRN(10)
    fs = 625e3
    Ns = fs / 125e3
    prn_seq = prn.prn_seq()
    prn_seq,b = ss.nrz_bits2(np.array(prn_seq), Ns)
    ref, rec = sim_shift(prn_seq, center, corr_length, shift=shift)
    ref_quant = quantize(ref, 12)
    rec_quant = quantize(rec, 12)
    return ref_quant, rec_quant


@cocotb.test()
async def verify_caf_slice(dut):
    clock = Clock(dut.clk, period=10, units='ns')

    # TODO: Add required test fixture variables above
    cocotb.start_soon(clock.start(start_high=False))

    assert dut.s_axis_tready.value == 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tready.value == 1

    for _ in range(0, 10):
        await RisingEdge(dut.clk)


def test_via_cocotb():
    with TemporaryDirectory() as tmpdir:
        ref_quant, rec_quant = generate_test_signals(default_shift)
        caf_slice = CAFSlice(ref_quant, rec_quant, freq_res=freq_res, n_bits=n_bits, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % caf_slice.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=caf_slice.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=False,
            build_args=["--trace", "--trace-structs", "--threads", str(get_sim_cpus())]
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module='test_caf_slice', waves=True)
