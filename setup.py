"""
Setup for pymeshfix
"""
from io import open as io_open
import sys
import os

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext

if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins

filepath = os.path.dirname(__file__)

# change path if necessary
if filepath:
    old_path = os.getcwd()
    os.chdir(filepath)

# Define macros for cython
macros = []
if os.name == 'nt':  # windows
    extra_compile_args = ['/openmp', '/O2', '/w', '/GS']
    extra_link_args = []
elif os.name == 'posix':  # linux org mac os
    if sys.platform == 'linux':
        extra_compile_args = ['-std=gnu++11', '-O3', '-w']
    else:  # probably mac os
        extra_compile_args = ['-O3', '-w']
else:
    raise Exception('Unsupported OS %s' % os.name)


# Check if 64-bit
if sys.maxsize > 2**32:
    macros.append(('IS64BITPLATFORM', None))


# Get version from version info
__version__ = None
version_file = os.path.join(filepath, 'pymeshfix', '_version.py')
with io_open(version_file, mode='r') as fd:
    exec(fd.read())

# readme file
readme_file = os.path.join(filepath, 'README.rst')

# for: the cc1plus: warning: command line option '-Wstrict-prototypes'
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # prevent numpy from thinking it is still in its setup process:
        try:
            del builtins.__NUMPY_SETUP__
        except AttributeError:
            pass
        import numpy
        self.include_dirs.append(numpy.get_include())

    def build_extensions(self):
        try:
            self.compiler.compiler_so.remove("-Wstrict-prototypes")
        except (AttributeError, ValueError):
            pass
        _build_ext.build_extensions(self)

try:
    import numpy
except ImportError:
    build_requires = ['numpy']
else:
    build_requires = []


setup(
    name='pymeshfix',
    packages=['pymeshfix', 'pymeshfix/examples'],
    version=__version__,
    description='Repairs triangular meshes',
    long_description=open(readme_file).read(),
    author='Alex Kaszynski',
    author_email='akascap@gmail.com',
    license='MIT',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7'],
    url='https://github.com/akaszynski/pymeshfix',

    # Build cython modules
    cmdclass={'build_ext': build_ext},
    ext_modules=[Extension("pymeshfix._meshfix",
                           ['pymeshfix/cython/meshfix.cpp',
                            'pymeshfix/cython/tin.cpp',
                            'pymeshfix/cython/checkAndRepair.cpp',
                            'pymeshfix/cython/coordinates.cpp',
                            'pymeshfix/cython/detectIntersections.cpp',
                            'pymeshfix/cython/edge.cpp',
                            'pymeshfix/cython/graph.cpp',
                            'pymeshfix/cython/heap.cpp',
                            'pymeshfix/cython/holeFilling.cpp',
                            'pymeshfix/cython/io.cpp',
                            'pymeshfix/cython/jqsort.cpp',
                            'pymeshfix/cython/list.cpp',
                            'pymeshfix/cython/marchIntersections.cpp',
                            'pymeshfix/cython/matrix.cpp',
                            'pymeshfix/cython/orientation.c',
                            'pymeshfix/cython/point.cpp',
                            'pymeshfix/cython/tmesh.cpp',
                            'pymeshfix/cython/triangle.cpp',
                            'pymeshfix/cython/vertex.cpp',
                            'pymeshfix/cython/_meshfix.pyx'],
                           language='c++',
                           extra_compile_args=extra_compile_args,
                           define_macros=macros)],

    keywords='meshfix',
    package_data={'pymeshfix/examples': ['StanfordBunny.ply']},
    install_requires=['numpy>1.11.0',
                      'pyvista>=0.19.0']
)

# revert to prior directory
if filepath:
    os.chdir(old_path)
