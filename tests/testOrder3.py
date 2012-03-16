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
         __init__.py (*)
      f9.py
dir2/ (prepended after finder is created)
   f4.py (*)
   f6/
       __init__.py (*)
   f6.py
dir3/ (appended after f4 is imported)
   f5.py
   f7/
      __init__.py (*)
   f7.py

f1.so and f2.so are both C-extensions, so they need to be compiled first. From
inside dir1, execute "python setup.py build_ext --inplace" to build these
modules.

This test just checks the __file__ and __loader__ attributes of a module, not
whether the loaded modules function correctly.
"""

import sys,os
scriptpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(scriptpath)) # path to cached_import.py
dir1 = os.path.join(scriptpath,"dir1")
dir2 = os.path.join(scriptpath,"dir2")
dir3 = os.path.join(scriptpath,"dir3")
sys.path.append(dir1)
from cached_import import simple_finder
my_importer = simple_finder()
sys.meta_path.append(my_importer)

import f1
import f2
import f3
sys.path.insert(0,dir2)
import f4
sys.path.append(dir3)
import f5
import f6
import f7
from f8 import f9

def check(modules):
    # For Python source files, either the source or bytecode file
    # could have been loaded.
    correct = { "f1" : [os.path.join(dir1,"f1","__init__.py"),
                        os.path.join(dir1,"f1","__init__.pyc"),
                        os.path.join(dir1,"f1","__init__.pyo")],
                "f2" : [os.path.join(dir1,"f2.so")],
                "f3" : [os.path.join(dir1,"f3.py"),
                        os.path.join(dir1,"f3.pyc"),
                        os.path.join(dir1,"f3.pyo")],
                "f4" : [os.path.join(dir2,"f4.py"),
                        os.path.join(dir2,"f4.pyc"),
                        os.path.join(dir2,"f4.pyo")],
                "f5" : [os.path.join(dir1,"f5.py"),
                        os.path.join(dir1,"f5.pyc"),
                        os.path.join(dir1,"f5.pyo")],
                "f6" : [os.path.join(dir2,"f6","__init__.py"),
                        os.path.join(dir2,"f6","__init__.pyc"),
                        os.path.join(dir2,"f6","__init__.pyo")],
                "f7" : [os.path.join(dir3,"f7","__init__.py"),
                        os.path.join(dir3,"f7","__init__.pyc"),
                        os.path.join(dir3,"f7","__init__.pyo")],
                "f8.f9" : [os.path.join(dir1,"f8","f9","__init__.py"),
                        os.path.join(dir1,"f8","f9","__init__.pyc"),
                        os.path.join(dir1,"f8","f9","__init__.pyo")],
                }
    alltests = True
    for mod in modules:
        match = False
        for fname in correct[mod.__name__]:
            if os.path.exists (fname) and os.path.samefile(mod.__file__,fname):
                match = True
                break
        ldr = getattr(mod,"__loader__",None)
        if not match or ldr != my_importer:
            print "FAILED:",mod.__name__,mod.__file__,ldr
            alltests = False
    if alltests:
        print "All tests passed."

check([f1,f2,f3,f4,f5,f6,f7,f9])
