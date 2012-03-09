"""Make sure we can import NumPy
"""
import sys,os
scriptpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(scriptpath)) # path to cached_import.py
from cached_import import finder
sys.meta_path.append(finder())
import numpy
# What did we import?
print numpy.__file__
print numpy.__version__
print getattr(numpy,"__loader__",None)
