from caf_verilog.caf import CAF
import pathlib
import os
import unittest
from caf_verilog.sim_helper import sim_get_runner
import glob

from caf_verilog.sim_helper import sim_shift
import numpy as np
from gps_helper.prn import PRN
from sk_dsp_comm import sigsys as ss
from sk_dsp_comm import digitalcom as dc


class TestBuildCAF(unittest.TestCase):

    def test_build_caf(self):
        prn = PRN(10)
        prn_seq = prn.prn_seq()
        prn_seq = [*prn_seq, *prn_seq]
        fs = 625e3
        Ns = fs / 200e3
        prn_seq, _ = ss.nrz_bits2(np.array(prn_seq), Ns)
        f_size = 24
        foas = np.arange(-f_size, f_size + 1) * 1000

        # Verify test vector length
        assert len(prn_seq) == 6138

        center = 3000
        corr_length = 1000
        shift = 25
        ncorr = np.arange(0, corr_length * 2)
        foa_offset = 16
        theta_shift = np.exp(1j*2*np.pi*ncorr*(foas[foa_offset])/float(fs))
        ref, rec = sim_shift(prn_seq, center, corr_length, shift=shift)
        output_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'caf_v')
        pathlib.Path(output_dir).mkdir(exist_ok=True)
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
            always=True,
        )


if __name__ == '__main__':
    unittest.main()
