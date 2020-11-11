from unittest import TestCase
from .. import capture_buffer as capt_buff
from tempfile import mkdtemp
import os


class TestCaptureBuffer(TestCase):

    def test_capture_buffer(self):
        tmpdir = mkdtemp()
        cb = capt_buff.CaptureBuffer(100, output_dir=tmpdir)
        cb.gen_tb()
        files = os.listdir(tmpdir)
        test_files = ['capture_buffer.v', 'capture_buffer_tb.v', 'capture_buffer_values.txt']
        for file in test_files:
            self.assertIn(file, files)

    def test_capture_buffer_values_file(self):
        tmpdir = mkdtemp()
        cb = capt_buff.CaptureBuffer(100, output_dir=tmpdir)
        with open(os.path.join(tmpdir, 'capture_buffer_values.txt')) as cbv:
            lines = len(cbv.readlines())
            self.assertEqual(100, lines)
