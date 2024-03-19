import pathlib
import os
import unittest
import glob

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from caf_verilog.sim_helper import sim_shift, sim_get_runner, get_sim_cpus
import numpy as np
from gps_helper.prn import PRN
from sk_dsp_comm import sigsys as ss
from sk_dsp_comm import digitalcom as dc

from caf_verilog.caf import CAF, set_increment_values

prn = PRN(10)
prn_seq = prn.prn_seq()
prn_seq = [*prn_seq, *prn_seq]
fs = 625e3
Ns = fs / 200e3
prn_seq, _ = ss.nrz_bits2(np.array(prn_seq), Ns)
foas = np.array([-20e3, 0, 20e3])

center = 3000
corr_length = 1000
shift = 25
ncorr = np.arange(0, corr_length * 2)
foa_offset = 1
theta_shift = np.exp(1j * 2 * np.pi * ncorr * (foas[foa_offset]) / float(fs))
ref, rec = sim_shift(prn_seq, center, corr_length, shift=shift)
output_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'caf_v')
pathlib.Path(output_dir).mkdir(exist_ok=True)
caf = CAF(ref, rec * theta_shift, foas, fs=fs, n_bits=8, ref_i_bits=8, rec_i_bits=8, output_dir=output_dir)


@cocotb.test()
async def caf_correlation(dut):

    clock = Clock(dut.clk, period=10, units='ns')

    cocotb.start_soon(clock.start(start_high=False))

    for _ in range(0, 5):
        await RisingEdge(dut.clk)

    assert dut.m_axis_freq_step_tready.value == 1
    assert dut.freq_step_index.value == 0

    await set_increment_values(caf, dut)

    


def test_via_cocotb():
    caf = CAF(ref, rec * theta_shift, foas, fs=fs, n_bits=8, ref_i_bits=8, rec_i_bits=8, output_dir=output_dir)
    verilog_sources = [os.path.join(output_dir, filename) for filename in glob.glob("%s/*.v" % output_dir)]
    runner = sim_get_runner()
    hdl_toplevel = "%s" % caf.module_name()
    caf_params = caf.params_dict()
    runner.build(
        verilog_sources=verilog_sources,
        parameters=caf_params,
        vhdl_sources=[],
        hdl_toplevel=hdl_toplevel,
        always=False,
        build_args=["--trace", "--trace-structs", "--threads", str(get_sim_cpus())]
    )
    runner.test(hdl_toplevel=hdl_toplevel, test_module='test_sim_caf_foas', waves=True)


if __name__ == '__main__':
    unittest.main()
