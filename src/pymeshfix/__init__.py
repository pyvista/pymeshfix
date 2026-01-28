"""PyMeshFix module."""

from importlib.metadata import PackageNotFoundError, version

from pymeshfix._meshfix import PyTMesh, clean_from_arrays, clean_from_file
from pymeshfix.meshfix import MeshFix

try:
    __version__ = version("pymeshfix")
except PackageNotFoundError:
    __version__ = "unknown"


__all__ = ["MeshFix", "PyTMesh", "clean_from_arrays", "clean_from_file", "__version__"]
