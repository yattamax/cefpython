from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import sys
import platform
from Cython.Compiler import Options

# Stop on first error, otherwise hundreds of errors appear in the console.
Options.fast_fail = True

# Written to cython_includes/compile_time_constants.pxi
CEF_VERSION = 3

"""
Building libcef_dll_wrapper
---------------------------

libcef_dll_wrapper needs to be compiled with /MD, otherwise you get linker errors
of type "already defined". When you try to compile using /MD you may get warnings:

  warning C4275: non dll-interface class 'stdext::exception' used as base for
  dll-interface class 'std::bad_typeid' see declaration of 'stdext::exception'
  see declaration of 'std::bad_typeid'

Which results in build errors. To solve it you need to add command line option:

  -D_HAS_EXCEPTIONS=1

Enabling C++ exceptions ("/EHsc") is not required.
"""

# Python version string: "27" or "32".
PYTHON_VERSION = str(sys.version_info.major) + str(sys.version_info.minor)

def CompileTimeConstants():

    print("Generating: cython_includes/compile_time_constants.pxi")
    with open("./../../../cython_includes/compile_time_constants.pxi", "w") as fd:
        fd.write('# This file was generated by setup.py\n')
        # A way around Python 3.2 bug: UNAME_SYSNAME is not set.
        fd.write('DEF UNAME_SYSNAME = "%s"\n' % platform.uname()[0])
        fd.write('DEF CEF_VERSION = %s\n' % CEF_VERSION)
        fd.write('DEF PY_MAJOR_VERSION = %s\n' % sys.version_info.major)

CompileTimeConstants()

ext_modules = [Extension(

    "cefpython_py%s" % PYTHON_VERSION,
    ["cefpython.pyx"],

    cython_directives={
        # Any conversion to unicode must be explicit using .decode().
        "c_string_type": "bytes",
        "c_string_encoding": "utf-8",
    },

    language='c++',
    
    include_dirs=[
        r'./../', 
        r'./../../', 
        r'./../../../', 
        r'./../../../cython_includes/'],

    library_dirs=[
        r'./',
        r"c:/Program Files (x86)/Windows Kits/8.0/Lib/win8/um/x86/",
        r'./../../client_handler/Release_py%s/' % PYTHON_VERSION,
        r'./../../subprocess/Release_libcefpythonapp_py%s/' % PYTHON_VERSION,
    ],

    libraries=[
        'libcef',
        'libcef_dll_wrapper',
        'User32',
        'client_handler_py%s' % PYTHON_VERSION, # Build with /MD.
        'libcefpythonapp_py%s' % PYTHON_VERSION,
    ],

    # /EHsc - using STL string, multimap and others that use C++ exceptions.
    extra_compile_args=['/EHsc'],

    # '/ignore:4217' - silence warnings: "locally defined symbol _V8FunctionHandler_Execute
    #                  imported in function "public: virtual bool __thiscall V8FunctionHandler::Execute".
    #                  client_handler or other vcprojects include setup/cefpython.h,
    #                  this is a list of functions with "public" statement that is
    #                  accessible from c++.
    extra_link_args=['/ignore:4217']
)]

setup(
    name = 'cefpython_py%s' % PYTHON_VERSION,
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
