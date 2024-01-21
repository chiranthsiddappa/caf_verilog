from caf_verilog.xcorr import XCorr
from tempfile import TemporaryDirectory
import os
import pathlib
from caf_verilog.sim_helper import sim_get_runner
import glob
import numpy as np

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from sk_dsp_comm import sigsys as ss
from gps_helper.prn import PRN


def generate_test_signals():
    prn = PRN(10)
    prn2 = PRN(20)
    fs = 625e3
    Ns = fs / 125e3
    prn_seq = prn.prn_seq()
    prn_seq2 = prn2.prn_seq()
    prn_seq,b = ss.nrz_bits2(np.array(prn_seq), Ns)
    prn_seq2,b2 = ss.nrz_bits2(np.array(prn_seq2), Ns)
    return prn_seq, prn_seq2


@cocotb.test()
async def verify_xcorr_via_prn(dut):
    prn_seq, prn_seq2 = generate_test_signals()
    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')
    
    cocotb.start_soon(clock.start(start_high=False))
    dut.m_axis_tvalid.value == 0
    dut.m_axis_tready.value == 0

    await RisingEdge(dut.clk)
    assert dut.s_axis_tready.value == 0
    assert dut.s_axis_tvalid.value == 0


def test_via_cocotb():
    with TemporaryDirectory() as tmpdir:
        prn_seq, prn_seq2 = generate_test_signals()
        x_corr = XCorr(ref=prn_seq, rec=prn_seq2, output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        runner = sim_get_runner()
        hdl_toplevel = "%s" % x_corr.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=x_corr.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True
        )
        runner.test(hdl_toplevel=hdl_toplevel, test_module="test_xcorr")


if __name__ == '__main__':
    test_via_cocotb()
