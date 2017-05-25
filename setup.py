import sys, os

from setuptools import setup, Extension
from Cython.Distutils import build_ext

import numpy

# Define macros for cython
macros = []
extra_args = []

# Check if 64-bit
if sys.maxsize > 2**32:
    macros.append(('IS64BITPLATFORM', None))

# Check if Windows
if not os.name == 'nt':
    extra_args.append('-std=gnu++11')
    # extra_args.append('-std=c++11') # might have to use this instead

# Files for Meshfix and cython wrapper
files = []

setup(
    name='pymeshfix',
    packages = ['pymeshfix', 'pymeshfix.Tests'],

    # Version
    version='0.10.1',

    description='Repairs triangular meshes',
    long_description=open('README.rst').read(),

    # Author details
    author='Alex Kaszynski',
    author_email='akascap@gmail.com',

#    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',

        # Target audience
        'Intended Audience :: Science/Research',

        # MIT License
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Tested with on Python 2.7 and 3.5
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],

    # Website
    url = 'https://github.com/akaszynski/pymeshfix',

    # Build cython modules
    cmdclass={'build_ext': build_ext},
    ext_modules = [Extension("pymeshfix._meshfix", 
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
                             extra_compile_args=extra_args,
                             define_macros=macros),],
                     
                     
    keywords='meshfix',                           
                           
    include_dirs=[numpy.get_include()],
                  
    package_data={'pymeshfix.Tests': ['StanfordBunny.ply']},

    # Might work with earlier versions (untested)
    install_requires=['numpy>1.9.3', 'cython>0.23.1']

)
