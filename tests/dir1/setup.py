from distutils.core import setup, Extension
modulef1 = Extension('f1',sources=['f1mod.c','f1wrapper.c'])
modulef2 = Extension('f2',sources=['f2mod.c','f2wrapper.c'])
setup (name = 'Foo',
       version = '1.0',
       description = 'This is the Foo package',
       ext_modules = [modulef1,modulef2])

