"""Setup for pymeshfix."""

import os
import platform
import sys
from io import open as io_open

import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup
from wheel.bdist_wheel import bdist_wheel

filepath = os.path.dirname(__file__)

# Define macros for cython
macros = []
ext_kwargs = {}
setup_kwargs = {}
if os.name == "nt":  # windows
    extra_compile_args = ["/openmp", "/O2", "/w", "/GS"]
    extra_link_args = []
elif os.name == "posix":  # linux org mac os
    if sys.platform == "linux":
        extra_compile_args = ["-std=gnu++11", "-O3", "-w"]
    else:  # probably mac os
        extra_compile_args = ["-O3", "-w"]
else:
    raise Exception(f"Unsupported OS {os.name}")


# Check if 64-bit
if sys.maxsize > 2**32:
    macros.append(("IS64BITPLATFORM", None))


# https://github.com/joerick/python-abi3-package-sample/blob/main/setup.py
class bdist_wheel_abi3(bdist_wheel):  # noqa: D101
    def get_tag(self):  # noqa: D102
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            return "cp311", "abi3", plat

        return python, abi, plat


if sys.version_info.minor >= 11 and platform.python_implementation() == "CPython":
    # Can create an abi3 wheel (typed memoryviews first available in 3.11)!
    macros.append(("Py_LIMITED_API", "0x030B0000"))
    ext_kwargs["py_limited_api"] = True
    setup_kwargs["cmdclass"] = {"bdist_wheel": bdist_wheel_abi3}


# Get version from version info
__version__ = None
version_file = os.path.join(filepath, "pymeshfix", "_version.py")
with io_open(version_file, mode="r") as fd:
    exec(fd.read())

# readme file
readme_file = os.path.join(filepath, "README.rst")


setup(
    name="pymeshfix",
    packages=["pymeshfix", "pymeshfix/examples"],
    version=__version__,
    description="Repair triangular meshes using MeshFix",
    long_description=open(readme_file).read(),
    long_description_content_type="text/x-rst",
    author="PyVista Developers",
    author_email="info@pyvista.org",
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    python_requires=">=3.9",
    url="https://github.com/pyvista/pymeshfix",
    # Build cython modules
    ext_modules=cythonize(
        [
            Extension(
                "pymeshfix._meshfix",
                [
                    "pymeshfix/cython/meshfix.cpp",
                    "pymeshfix/cython/tin.cpp",
                    "pymeshfix/cython/checkAndRepair.cpp",
                    "pymeshfix/cython/coordinates.cpp",
                    "pymeshfix/cython/detectIntersections.cpp",
                    "pymeshfix/cython/edge.cpp",
                    "pymeshfix/cython/graph.cpp",
                    "pymeshfix/cython/heap.cpp",
                    "pymeshfix/cython/holeFilling.cpp",
                    "pymeshfix/cython/io.cpp",
                    "pymeshfix/cython/jqsort.cpp",
                    "pymeshfix/cython/list.cpp",
                    "pymeshfix/cython/marchIntersections.cpp",
                    "pymeshfix/cython/matrix.cpp",
                    "pymeshfix/cython/orientation.c",
                    "pymeshfix/cython/point.cpp",
                    "pymeshfix/cython/tmesh.cpp",
                    "pymeshfix/cython/triangle.cpp",
                    "pymeshfix/cython/vertex.cpp",
                    "pymeshfix/cython/_meshfix.pyx",
                ],
                language="c++",
                extra_compile_args=extra_compile_args,
                define_macros=macros,
                include_dirs=[np.get_include()],
                **ext_kwargs,
            )
        ]
    ),
    keywords="meshfix",
    package_data={"pymeshfix/examples": ["StanfordBunny.ply", "planar_mesh.ply"]},
    install_requires=["numpy>1.11.0", "pyvista>=0.30.0"],
    **setup_kwargs,
)
