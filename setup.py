from setuptools import setup
import os
import codecs
from caf_verilog import __version__


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return codecs.open(fpath(fname), encoding='utf-8').read()


requirements = read(fpath('requirements.txt'))

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='caf_verilog',
      version=__version__.__version__,
      description='CAF Verilog',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Chiranth Siddappa',
      author_email='chiranthsiddappa@gmail.com',
      url='https://github.com/chiranthsiddappa/caf_verilog',
      package_dir={'caf_verilog': 'caf_verilog'},
      packages=['caf_verilog'],
      license='MIT',
      install_requires=requirements.split(),
      test_suite='nose.collector',
      tests_require=['nose', 'tox', 'numpy'],
      extras_require={
      },
      python_requires='>=3.4',
      )
