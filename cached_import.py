"""This is an initial implementation of the finder/loader discussed at:
http://mail.scipy.org/pipermail/numpy-discussion/2012-March/061160.html

This is intended to take the place of MPI_Import.py. This version has
only been tested minimally, and is being made available primarily for
testing and preliminary benchmarking.

Known issues:
- Modules loaded via the Windows registry may be incorrectly hidden by
  a module of the same name in sys.path.
- If a file is added to a directory on sys.path, it won't be cached, so
  there may be precedence issues. If a file disappears or its permissions
  change, the import will fail.

To use, start a script off with the following:

import sys
from cached_import import finder # or mpi_finder
sys.meta_path.append(finder())   # or mpi_finder
"""

import imp,sys,os

class finder(object):
    def __init__(self,build=True):
        t = imp.get_suffixes()
        self._suffixes = [x[0] for x in t] # in order of precedence
        self._rsuffixes = self._suffixes[::-1] # and in reverse order
        self._suffix_tuples = dict((x[0],tuple(x)) for x in t)
        if build:
            self._syspath = list(sys.path)
            self._build_cache()
        else: # For some subclasses
            self._syspath = []
            self._cache = {}

    def _build_cache(self):
        """Traverse sys.path, building (or re-building) the cache."""
        import os
        self._cache = {}
        for d in sys.path:
            if os.path.isdir(d):
                self._process_dir(os.path.realpath(d))

    def find_module(self,fullname,path=None):
        """Return self if 'fullname' is in sys.path (and isn't a builtin or
        frozen module)."""
        # First, make sure our cache is up-to-date.
        if sys.path != self._syspath:
            stored_length = len(self._syspath)
            real_length = len(sys.path)
            # If sys.path isn't bigger, we need to rebuild the cache
            if real_length <= stored_length:
                self._build_cache()
            # Some directories were prepended to the path, so add them.
            elif self._syspath == sys.path[-stored_length:]:
                for d in sys.path[real_length-stored_length-1::-1]:
                    if os.path.isdir(d):
                        self._process_dir(os.path.realpath(d),prepend=True)
            # Directories appended to the path.
            elif self._syspath == sys.path[:len(self._syspath)]:
                for d in sys.path[stored_length-real_length:]:
                    if os.path.isdir(d):
                        self._process_dir(os.path.realpath(d))
            # Path otherwise modified, so we need to rebuild the cache.
            else:
                self._build_cache()
            self._syspath = list(sys.path)
            
        # Don't override builtin/frozen modules. TODO: Windows registry?
        if (fullname not in sys.builtin_module_names and
            not imp.is_frozen(fullname) and
            fullname in self._cache):
            # print "__IMPORTING ",fullname
            return self
        return None

    def load_module(self,fullname):
        """Load the module fullname using cached path."""
        if fullname in self._cache:
            if fullname in sys.modules:
                return sys.modules[fullname]
            pathname,desc = self._cache[fullname]
            # print "__LOADING ",fullname,pathname
            if os.path.isfile(pathname):
                # (If we're loading a PY_SOURCE file, the interpreter will
                # automatically check for a compiled (.py[c|o]) file.)
                with open(pathname,desc[1]) as f:
                    mod = imp.load_module(fullname,f,pathname,desc)
            # Not a file, so it's a package directory
            else:
                mod = imp.load_module(fullname,None,pathname,desc)
            mod.__loader__ = self
            return mod
        raise ImportError("This shouldn't happen!")


    # Build up a dict of modules (including package directories) found in a
    # directory. If this directory has been prepended to the path, we need to
    # overwrite any conflicting entries in the cache. To make sure precedence
    # is correct, we'll reverse the list of suffixes when we're prepending.
    #
    # Rather than add a lot of checks here to make sure we don't stomp on a
    # builtin module, we'll just reject these in find_module
    def _process_dir(self,dir,parent=None,prepend=False,visited=[]):
        """Process a directory dir, looking for valid modules.

        Arguments:
        dir -- (an absolute, real path to a directory)
        parent -- parent module, in the case where dir is a package directory
        prepend -- True if dir has just been prepended to sys.path. In that
                   case, we'll replace existing cached entries with the same
                   module name.
        visited -- list of the real paths of visited directories. Used to
                   prevent infinite recursion in the case of symlink cycles
                   in package subdirectories.
        """
        import stat

        # Avoid symlink cycles in a package.
        if dir in visited:
            return
        visited.append(dir)

        # All files and subdirs. Store the name and the path.
        try:
            contents = dict((x,os.path.join(dir,x))
                            for x in os.listdir(dir))
        # Unreadable directory, so skip
        except OSError:
            return
            
        # Split contents into files & subdirs (only stat each one once)
        files = {}
        subdirs = {}
        for entry in contents:
            try:
                mode = os.stat(contents[entry]).st_mode
            except OSError:
                return # couldn't read!
            # Checking whether these are readable using os.access
            # requires a second stat. Argh. It's tricky to get that
            # information directory from os.stat, though.
            if stat.S_ISDIR(mode) and os.access(contents[entry],os.R_OK):
                subdirs[entry] = contents[entry]
            elif stat.S_ISREG(mode) and os.access(contents[entry],os.R_OK):
                files[entry] = contents[entry]

        # Package directories have the highest precedence. But when prepend is
        # True, we need to reverse the order here. We'll do this with these
        # nested functions.
        def process_subdirs():
            for d in subdirs:
                fqname = parent+"."+d if parent else d # fully qualified name
                # A package directory must have an __init__.py.
                init_py = os.path.join(subdirs[d],"__init__.py")
                if (os.path.isfile(init_py)) and os.access(init_py,os.R_OK):
                    if fqname not in self._cache or prepend:
                        self._cache[fqname] = (subdirs[d],
                                               ('','',imp.PKG_DIRECTORY))
                        self._process_dir(os.path.join(dir,d),
                                          fqname,prepend,visited)

        def process_files():
            ordered_suffixes = self._rsuffixes if prepend else self._suffixes
            for s in ordered_suffixes:
                l = len(s)
                for f in files:
                    # Check for matching suffix.
                    if f[-l:] == s:
                        fqname = parent+"."+f[:-l] if parent else f[:-l]
                        if fqname not in self._cache or prepend:
                                self._cache[fqname] = (files[f],
                                                       self._suffix_tuples[s])

        if prepend:
            process_files()
            process_subdirs()
        else:
            process_subdirs()
            process_files()

                                
"""Finder that lets one MPI process do all of the initial caching.
"""
class mpi_finder(finder):        
    def __init__(self):
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        if rank == 0:
            finder.__init__(self)
        else:
            finder.__init__(self,False)
        self._syspath,self._cache = comm.bcast((self._syspath,self._cache))
                        
if __name__ == "__main__":
    import sys
    sys.meta_path.append(finder())
    import numpy
    # What did we import?
    print numpy.__file__,numpy.__version__

