"""
This file is needed to build the Python C extension as an .so file.
"""
from distutils.core import setup, Extension


module = Extension(
    'mything',
    include_dirs = ['./'],
    sources = ['mything.c', 'mythingmodule.c'])
 
setup (name = 'PackageName',
        version = '1.0',
        description = 'This is a demo package',
        ext_modules = [module])
