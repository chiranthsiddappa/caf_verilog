from caf_verilog.dot_prod_pip import DotProdPip
from caf_verilog.quantizer import quantize
from caf_verilog.sim_helper import sim_get_runner

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import glob
from tempfile import TemporaryDirectory
from gps_helper.prn import PRN
import numpy as np
from numpy import testing as npt
from sk_dsp_comm import sigsys as ss


def generate_test_signals():
    """
    PRN Sequence Generator
    """
    prn = PRN(15)
    prn2 = PRN(20)
    fs = 625e3
    Ns = fs / 125e3
    prn_seq = prn.prn_seq()
    prn_seq2 = prn2.prn_seq()
    prn_seq,b = ss.nrz_bits2(np.array(prn_seq), Ns)
    prn_seq2,b2 = ss.nrz_bits2(np.array(prn_seq2), Ns)
    return prn_seq, prn_seq2

@cocotb.test()
async def verify_cpx_calcs(dut):
    prn, prn2 = generate_test_signals()
    x_quant = quantize(prn, 12)
    y_quant = quantize(prn2, 12)
    zipped_input_values = list(zip(x_quant, y_quant))

    cpx_became_valid = False
    prod_became_valid = False
    max_length_counter = -1

    cpx_output_i = []
    cpx_output_q = []

    output_cap = []

    clock = Clock(dut.clk, 10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))

    await RisingEdge(dut.clk)
    dut.m_axis_product_tready.value = 0
    dut.m_axis_product_tready.value = 0
    dut.m_axis_x_tvalid.value = 0
    dut.m_axis_y_tvalid.value = 0
    assert dut.s_axis_product_tvalid.value == 0
    assert dut.length_counter.value.signed_integer == -1
    prev_length_counter = -1
    assert dut.length_counter_extended.value.signed_integer == -1


def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    with TemporaryDirectory() as tmpdir:
        prn_seq, prn_seq2 = generate_test_signals()
        dot_prod_pip = DotProdPip(prn_seq[:10], prn_seq2[:10], output_dir=tmpdir)
        verilog_sources = [os.path.join(tmpdir, filename) for filename in glob.glob("%s/*.v" % tmpdir)]
        assert len(verilog_sources) > 0
        runner = sim_get_runner()
        hdl_toplevel = "%s" % dot_prod_pip.module_name()
        runner.build(
            verilog_sources=verilog_sources,
            parameters=dot_prod_pip.params_dict(),
            vhdl_sources=[],
            hdl_toplevel=hdl_toplevel,
            always=True
        )
        runner.test(hdl_toplevel="%s" % dot_prod_pip.module_name(), test_module='test_dot_product_prn')

if __name__ == '__main__':
    test_via_cocotb()
