from distutils.core import setup, Extension
 
module = Extension('mything', sources = ['mythingmodule.c'])
 
setup (name = 'PackageName',
        version = '1.0',
        description = 'This is a demo package',
        ext_modules = [module])
