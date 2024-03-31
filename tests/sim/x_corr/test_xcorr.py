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

center = 300
corr_length = 250
shift = 25


def generate_test_signals():
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
async def verify_xcorr_via_prn(dut):
    ref_quant, rec_quant = generate_test_signals()
    ref_quant_tb, rec_quant_tb = gen_tb_values(ref_quant, rec_quant)
    input_val_pairs = list(zip(ref_quant_tb, rec_quant_tb))
    output_cap = []

    assert (len(input_val_pairs) % len(ref_quant)) == 0
    assert len(input_val_pairs) == (len(ref_quant)**2 + len(ref_quant))

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tvalid.value = 0
    dut.m_axis_tready.value = 0

    output_max, index = await send_and_receive(dut, ref_quant_tb, rec_quant_tb)

    index_to_verify = index.value
    assert index_to_verify == (corr_length / 2) - shift

    await RisingEdge(dut.clk)
    dut.m_axis_tready.value = 0

    for _ in range(0, 10):
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
            build_args=["--trace-fst", "--trace-structs", "--threads", str(get_sim_cpus())]
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module="test_xcorr")


if __name__ == '__main__':
    test_via_cocotb()
