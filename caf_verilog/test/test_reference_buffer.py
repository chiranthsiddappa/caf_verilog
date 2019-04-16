from unittest import TestCase
from .. import reference_buffer as ref_buff
from tempfile import mkdtemp
import os


class TestReferenceBuffer(TestCase):

    def test_reference_buffer(self):
        """
        Test that the files are written out for instantation and testbench.
        :return:
        """
        tmpdir = mkdtemp()
        x = [ii for ii in range(0, 10)]
        rb = ref_buff.ReferenceBuffer(x, output_dir=tmpdir)
        rb.gen_tb()
        files = os.listdir(tmpdir)
        test_files = ['reference_buffer.v', 'reference_buffer_tb.v', 'reference_buffer_values.txt']
        for file in test_files:
            self.assertIn(file, files)