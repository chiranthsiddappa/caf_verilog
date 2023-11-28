from cocotb.runner import get_runner, Simulator
import os

__hdl_toplevel_lang__ = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
__sim__ = os.getenv("SIM", "verilator")

def sim_get_runner() -> Simulator:
    return get_runner(__sim__)