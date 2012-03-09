"""Basic sanity check for the import order of cached_import.py.

Layout (*) indicates the module should be imported:

dir1/
   f1/ (*)
      __init__.py
   f1.so
   f1.py
   f2/
       (empty)
   f2.so (*)
   f2.py
   f3.py (*)
   f4.py
   f5.py (*)
   f8/
      __init__.py
      f9/
         __init__.py
      f9.py
dir2/ (prepended after finder is created)
   f4.py (*)
   f6/ (*)
       __init__.py
   f6.py
dir3/ (appended after f4 is imported)
   f5.py
   f7/ (*)
      __init__.py
   f7.py
   
"""

import sys,os
scriptpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(scriptpath)) # path to cached_import.py
dir1 = os.path.join(scriptpath,"dir1")
dir2 = os.path.join(scriptpath,"dir2")
dir3 = os.path.join(scriptpath,"dir3")
sys.path.append(dir1)
from cached_import import finder
sys.meta_path.append(finder())

# TODO: check that these are correct, instead of just printing stuff out.
import f1
print "f1",f1.__file__
import f2
print "f2",f2.__file__
import f3
print "f3",f3.__file__
sys.path.insert(0,dir2)
import f4
print "f4",f4.__file__
sys.path.append(dir3)
import f5
print "f5",f5.__file__
import f6
print "f6",f6.__file__
import f7
print "f7",f7.__file__
from f8 import f9
print "f9",f9.__file__
