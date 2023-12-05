
from caf_verilog.sig_gen import SigGen
import os
import cocotb
from cocotb.clock import Clock
from caf_verilog.sim_helper import sim_get_runner
from cocotb.triggers import RisingEdge
import glob

@cocotb.test()
async def gen_signal_via_sim(dut):
    output_file = open('sig_gen_output.txt', mode='+w')
    clock = Clock(dut.clk, 10, units="us")  # Create a 10ns period clock on port clk

    dut.freq_step = int('100000000', 2)
    dut.m_axis_data_tready = 0
    dut.m_axis_freq_step_tvalid = 0
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))

    dut.m_axis_data_tready = 1
    dut.m_axis_freq_step_tvalid = 1


    await RisingEdge(dut.clk)
    
    for i in range(0, 512*10):
        await RisingEdge(dut.clk)
        assert dut.s_axis_data_tvalid == 1
        if i == 0: # Make sure we start at cos 1, sine 0
            assert dut.cosine.value == 127 # 8 bits signed
            assert dut.sine.value == 0
        output_file.write("%s,%s\n" % (int(dut.cosine.value), int(dut.sine.value)))


def test_via_cocotb():
    """
    Main entry point for testing output via cocotb
    """
    sig_gen = SigGen(1200, 625e3, 8)
    verilog_sources = [os.path.join('.', filename) for filename in glob.glob("%s/*.v" % '.')]
    sig_gen.gen_tb()
    runner = sim_get_runner()
    hdl_toplevel = "%s" % sig_gen.sig_gen_name
    runner.build(
        verilog_sources=verilog_sources,
        parameters=sig_gen.params_dict(),
        vhdl_sources=[],
        hdl_toplevel=hdl_toplevel,
        always=True
    )
    runner.test(hdl_toplevel="%s" % sig_gen.sig_gen_name, test_module="test_sim_sig_gen,")

if __name__ == '__main__':
    test_via_cocotb()