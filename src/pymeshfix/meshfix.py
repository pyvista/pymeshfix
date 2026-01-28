"""Python module to interface with wrapped meshfix."""

from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import NDArray

from pymeshfix import _meshfix

if TYPE_CHECKING:
    from pyvista.core.pointset import PolyData


def _polydata_from_faces(points: NDArray[np.float64], faces: NDArray[np.int32]) -> "PolyData":
    """
    Generate a polydata from a faces array containing no padding and all triangles.

    Parameters
    ----------
    points : np.ndarray
        Points array.
    faces : np.ndarray
        ``(n, 3)`` faces array.

    Returns
    -------
    PolyData
        New mesh.

    """
    if find_spec("pyvista.core") is None:
        raise ModuleNotFoundError(
            "To use this feature install pyvista with:\n\n    `pip install pyvista"
        )

    from pyvista.core.pointset import PolyData
    from vtkmodules.util.numpy_support import numpy_to_vtk
    from vtkmodules.vtkCommonCore import vtkTypeInt32Array
    from vtkmodules.vtkCommonDataModel import vtkCellArray

    if faces.ndim != 2:
        raise ValueError("Expected a two dimensional face array.")

    pdata = PolyData()
    pdata.points = points

    # convert to vtk arrays without copying
    vtk_dtype = vtkTypeInt32Array().GetDataType()

    offset = np.arange(0, faces.size + 1, faces.shape[1], dtype=np.int32)
    offset_vtk = numpy_to_vtk(offset, deep=False, array_type=vtk_dtype)
    faces_vtk = numpy_to_vtk(faces.ravel(), deep=False, array_type=vtk_dtype)

    carr = vtkCellArray()
    carr.SetData(offset_vtk, faces_vtk)

    pdata.SetPolys(carr)
    return pdata


class MeshFix:
    """Clean and tetrahedralize surface meshes using MeshFix.

    Parameters
    ----------
    args : pyvista.PolyData | (np.ndarray, np.ndarray)
        Either a pyvista surface mesh :class:`pyvista.PolyData` or a ``n x 3``
        vertex array and ``n x 3`` face array (indices of the triangles).

    Examples
    --------
    Create a meshfix object from a pyvista mesh.

    >>> from pyvista import examples
    >>> from pymeshfix import MeshFix
    >>> cow = examples.download_cow()
    >>> mfix = MeshFix(cow)

    Create a meshfix object from two numpy arrays. This example is incomplete
    as it does not contain the entire array.

    >>> import numpy as np
    >>> points = np.array(
    ...     [
    ...         [3.71636, 2.343387, 0.0],
    ...         [4.126565, 0.642027, 0.0],
    ...         [3.454971, 2.169877, 0.0],
    ...         ...,
    ...         [4.12616, 2.12093, 1.17252],
    ...         [4.133175, 2.175231, 1.259323],
    ...         [4.232341, 1.903079, 0.534362],
    ...     ],
    ...     dtype=float32,
    ... )
    >>> faces = np.array(
    ...     [
    ...         [210, 252, 251],
    ...         [250, 251, 252],
    ...         [201, 253, 210],
    ...         ...,
    ...         [1965, 2193, 2194],
    ...         [2391, 2398, 970],
    ...         [966, 961, 970],
    ...     ]
    ... )
    >>> mfix = MeshFix(points, faces)

    """

    def __init__(self, *args):
        """Initialize meshfix."""
        pv_installed = find_spec("pyvista.core")

        if isinstance(args[0], np.ndarray):
            self.load_arrays(args[0], args[1])
        elif pv_installed:
            import pyvista.core as pv

            if isinstance(args[0], pv.PolyData):
                mesh = pv.wrap(args[0])
                self.v = mesh.points.astype(np.float64, copy=False)

                # check if triangular mesh
                if not mesh.is_all_triangles:
                    mesh = mesh.triangulate()

                self.f = mesh._connectivity_array.reshape(-1, 3).astype(np.int32, copy=False)

        else:
            raise TypeError("Invalid input. Please load a surface mesh or face and vertex arrays")

    def load_arrays(self, v: NDArray[np.float64], f: NDArray[np.int32]) -> None:
        """
        Load triangular mesh from vertex and face numpy arrays.

        Both vertex and face arrays should be 2D arrays with each vertex
        containing XYZ data and each face containing three points.

        Parameters
        ----------
        v : np.ndarray[np.float64]
            ``(n, 3)`` vertex array.
        f : np.ndarray[np.int32]
            ``(m, 3)`` face array.

        Examples
        --------
        Create a meshfix object from two numpy arrays. This example is incomplete
        as it does not contain the entire array.

        >>> from pymeshfix import MeshFix
        >>> import numpy as np
        >>> points = np.array(
        ...     [
        ...         [3.71636, 2.343387, 0.0],
        ...         [4.126565, 0.642027, 0.0],
        ...         [3.454971, 2.169877, 0.0],
        ...         ...,
        ...         [4.12616, 2.12093, 1.17252],
        ...         [4.133175, 2.175231, 1.259323],
        ...         [4.232341, 1.903079, 0.534362],
        ...     ],
        ...     dtype=float32,
        ... )
        >>> faces = np.array(
        ...     [
        ...         [210, 252, 251],
        ...         [250, 251, 252],
        ...         [201, 253, 210],
        ...         ...,
        ...         [1965, 2193, 2194],
        ...         [2391, 2398, 970],
        ...         [966, 961, 970],
        ...     ]
        ... )
        >>> mfix = MeshFix(points, faces)

        """
        # Check inputs
        if not isinstance(v, np.ndarray):
            try:
                v = np.asarray(v, np.float64)  # will not copy if correct type
                if v.ndim != 2 and v.shape[1] != 3:
                    raise ValueError(
                        f"Invalid vertex shape {v.shape}.  Shape should be (npoints, 3)"
                    )
            except BaseException:
                raise ValueError("Unable to convert vertex input to valid numpy array.")

        if not isinstance(f, np.ndarray):
            try:
                f = np.asarray(f, np.int32)  # will not copy if correct type
                if f.ndim != 2 and f.shape[1] != 3:
                    raise ValueError(
                        f"Invalid faces array shape {f.shape}.  Shape should be (n_faces, 3)"
                    )
            except BaseException:
                raise ValueError("Unable to convert face input to valid numpy array.")

        self.v = v
        self.f = f

    @property
    def mesh(self) -> "PolyData":
        """
        Return the surface mesh.

        Returns
        -------
        pyvista.PolyData
            Surface mesh as a PolyData object.

        Examples
        --------
        Create a meshfix object from a pyvista mesh.

        >>> from pyvista import examples
        >>> from pymeshfix import MeshFix
        >>> cow = examples.download_cow()
        >>> mfix = MeshFix(cow)
        >>> mfix.mesh
        PolyData (0x7fa3c735f8e0)
          N Cells:    5804
          N Points:   2903
          N Strips:   0
          X Bounds:   -4.446e+00, 5.998e+00
          Y Bounds:   -3.637e+00, 2.760e+00
          Z Bounds:   -1.701e+00, 1.701e+00
          N Arrays:   0

        Access the underlying mesh and plot it.

        >>> mfix.mesh.plot()

        Access the underlying mesh and export it.

        >>> mfix.mesh.save("my_mesh.ply")

        """
        return _polydata_from_faces(self.v, self.f)

    def extract_holes(self) -> "PolyData":
        """Extract the boundaries of the holes in this mesh to a new PyVista mesh of lines."""
        return self.mesh.extract_feature_edges(
            boundary_edges=True, feature_edges=False, manifold_edges=False
        )

    @property
    def points(self) -> NDArray[np.float64]:
        """
        Return the points of the mesh.

        Returns
        -------
        numpy.ndarray
            The points of the mesh.

        Examples
        --------
        Generate a MeshFix object and return the points.

        >>> from pyvista import examples
        >>> from pymeshfix import MeshFix
        >>> cow = examples.download_cow()
        >>> mfix = MeshFix(cow)
        >>> mfix.points
        pyvista_ndarray([[3.71636 , 2.343387, 0.      ],
                         [4.126565, 0.642027, 0.      ],
                         [3.454971, 2.169877, 0.      ],
                         ...,
                         [4.12616 , 2.12093 , 1.17252 ],
                         [4.133175, 2.175231, 1.259323],
                         [4.232341, 1.903079, 0.534362]], dtype=float32)

        """
        return self.v

    @property
    def faces(self) -> NDArray[np.int32]:
        """
        Return the indices of the faces of the mesh.

        Returns
        -------
        numpy.ndarray
            The points of the mesh.

        Examples
        --------
        Generate a MeshFix object and return the points.

        >>> from pyvista import examples
        >>> from pymeshfix import MeshFix
        >>> cow = examples.download_cow()
        >>> mfix = MeshFix(cow)
        >>> mfix.faces
        array([[ 210,  252,  251],
               [ 250,  251,  252],
               [ 201,  253,  210],
               ...,
               [1965, 2193, 2194],
               [2391, 2398,  970],
               [ 966,  961,  970]])

        """
        return self.f

    def plot(self, show_holes: bool = True, **kwargs: Any):
        """Plot the mesh.

        Parameters
        ----------
        show_holes : bool, default: True
            Shows boundaries.

        **kwargs : keyword arguments
            Additional keyword arguments.  See :func:`pyvista.plot`.

        Examples
        --------
        Load the example bunny mesh and plot it.

        >>> from pyvista import examples
        >>> from pymeshfix import MeshFix
        >>> mesh = examples.download_bunny()
        >>> mfix = MeshFix(mesh)
        >>> mfix.plot(show_holes=True)

        """
        try:
            import pyvista as pv
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Install pyvista to use this feature")

        if show_holes:
            edges = self.extract_holes()

            off_screen = kwargs.pop("off_screen", False)
            screenshot = kwargs.pop("screenshot", None)

            plotter = pv.Plotter(off_screen=off_screen)
            if "cpos" in kwargs:
                plotter.camera_position = kwargs.pop("cpos", None)
            plotter.add_mesh(self.mesh, label="mesh", **kwargs)
            if edges.n_points:
                plotter.add_mesh(edges, "r", label="edges")
                plotter.add_legend()  # ty: ignore[missing-argument]
            return plotter.show(screenshot=screenshot)

        return self.mesh.plot(**kwargs)

    def repair(
        self, verbose: bool = False, joincomp: bool = False, remove_smallest_components: bool = True
    ) -> None:
        """Perform mesh repair using MeshFix's default repair process.

        Parameters
        ----------
        verbose : bool, default: False
            Enables or disables debug printing.
        joincomp : bool, default: False
            Attempts to join nearby open components.
        remove_smallest_components : bool, default: True
            Remove all but the largest isolated component from the mesh before
            beginning the repair process.

        Notes
        -----
        Vertex and face arrays are updated inplace. Access them with:

        * :attr:`Meshfix.points`
        * :attr:`Meshfix.faces`

        Examples
        --------
        Repair using the verbose option.

        >>> from pyvista import examples
        >>> from pymeshfix import MeshFix
        >>> mesh = examples.download_bunny()
        >>> mfix = MeshFix(mesh)
        >>> mfix.repair(verbose=True)
        >>> mfix.plot(show_holes=True)

        """
        self.v, self.f = _meshfix.clean_from_arrays(
            self.v, self.f, verbose, joincomp, remove_smallest_components
        )

    def save(self, filename: str | Path, binary=True):
        """
        Write the points and faces as a surface mesh to disk using PyVista.

        This is a a simple wrapper for
        :pyvista:`pyvista.PolyData.save`.

        Parameters
        ----------
        filename : str
            Filename of mesh to be written. Filetype is inferred from
            the extension of the filename unless overridden with
            ftype. Generally one of the following types:

            - ``".ply"``
            - ``".stl"``
            - ``".vtk"``
        binary: bool, default: True
            Write the file using a binary writer. Binary files read and write
            much faster than ASCII.

        """
        return self.mesh.save(filename, binary)
