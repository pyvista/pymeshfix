"""Python module to interface with wrapped meshfix."""

from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import NDArray

from pymeshfix import _meshfix

if TYPE_CHECKING:
    from pyvista.core.pointset import PolyData


class InvalidMeshFixInputError(TypeError):
    def __init__(self, message=None):
        if message is None:
            message = (
                "Invalid input. Please input a surface mesh, vertex and face arrays, or a "
                "file name. Note that pyvista is required when loading anything other "
                "than arrays."
            )
        super().__init__(message)


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
    args : pyvista.PolyData | (np.ndarray, np.ndarray) | pathlib.Path | str
        Either a pyvista surface mesh :class:`pyvista.PolyData` or a ``n x 3``
        vertex array and ``n x 3`` face array (indices of the triangles). Also
        supports reading directly from a file.
    verbose : bool, default: False
        Set this to ``True`` to enable additional output from MeshFix.

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

    def __init__(self, *args, verbose: bool = False):
        """Initialize meshfix."""
        pv_installed = find_spec("pyvista.core")
        self._mfix = _meshfix.PyTMesh()
        self._mfix.set_quiet(not verbose)

        if len(args) == 0:
            raise InvalidMeshFixInputError()

        if isinstance(args[0], np.ndarray):
            if len(args) != 2 or not isinstance(args[1], np.ndarray):
                raise TypeError("If first argument is an array, second argument must be an array")
            self.load_arrays(args[0], args[1])
        elif pv_installed:
            import pyvista.core as pv

            if isinstance(args[0], pv.PolyData):
                mesh = pv.wrap(args[0])

            elif isinstance(args[0], (Path, str)):
                mesh = pv.read(args[0])
                if not isinstance(mesh, pv.PolyData):
                    raise InvalidMeshFixInputError(
                        f"Expected to load a `pyvista.PolyData` from file, but got `{type(mesh)}`"
                    )
            else:
                InvalidMeshFixInputError(
                    "Invalid input. Please input a surface mesh, vertex and face arrays, or a"
                    " file name."
                )
            v = mesh.points.astype(np.float64, copy=False)

            # check if triangular mesh
            if not mesh.is_all_triangles:
                mesh = mesh.triangulate()

            f = mesh._connectivity_array.reshape(-1, 3).astype(np.int32, copy=False)
            self.load_arrays(v, f)

        else:
            raise InvalidMeshFixInputError()

    @property
    def n_boundaries(self) -> int:
        """Return the number of boundaries (holes) in this mesh."""
        return self._mfix.n_boundaries

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
        self._mfix.load_array(
            v.astype(np.float64, copy=False),
            f.astype(np.int32, copy=False),
        )

    def _return_arrays(self) -> tuple[NDArray[np.float64], NDArray[np.int32]]:
        """
        Return the arrays from the mesh fix instance.

        Returns
        -------
        np.ndarray[np.float64]
            Array of points shaped ``(n, 3)``.
        np.ndarray[np.float64]
            Array of faces shaped ``(m, 3)``.

        """
        return self._mfix.return_arrays()

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
        return _polydata_from_faces(self.points, self.faces)

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
        return self._mfix.return_points()

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
        return self._mfix.return_faces()

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
        self,
        joincomp: bool = False,
        remove_smallest_components: bool = True,
    ) -> None:
        """
        Perform mesh repair using MeshFix's default repair process.

        Parameters
        ----------
        fill_holes : bool, default: True
            Call meshfix's internal ``fill_small_boundaries``.
        joincomp : bool, default: False
            Attempts to join nearby open components.
        remove_smallest_components : bool, default: True
            Remove all but the largest isolated component from the mesh before
            beginning the repair process.

        Notes
        -----
        Vertex and face arrays can be accessed from:

        * :attr:`Meshfix.points`
        * :attr:`Meshfix.faces`

        You can alternatively call individual repair functions if you desire
        specific fixes. For example :func:`MeshFix.fill_holes`.

        Examples
        --------
        Repair using the verbose option.

        >>> from pyvista import examples
        >>> from pymeshfix import MeshFix
        >>> mesh = examples.download_bunny()
        >>> mfix = MeshFix(mesh, verbose=True)
        >>> mfix.repair()
        >>> mfix.plot(show_holes=True)

        """
        self._mfix.fill_small_boundaries(0, True)
        if joincomp:
            self._mfix.join_closest_components()
        if remove_smallest_components:
            self._mfix.remove_smallest_components()
        self._mfix.clean()

    def fill_holes(self, n_edges: int = 0, refine: bool = True) -> int:
        """
        Fill small boundary loops (holes) in the mesh.

        Parameters
        ----------
        nbe : int, default: 0
            Maximum number of boundary edges to fill. If 0, fill all.
        refine : bool, default: True
            Refine filled regions.

        Returns
        -------
        int
            Number of holes filled.

        """
        return self._mfix.fill_small_boundaries(n_edges, refine)

    def join_closest_components(self) -> None:
        """Attempt to join nearby open components."""
        self._mfix.join_closest_components()

    def remove_smallest_components(self) -> None:
        """Remove all but the largest connected component."""
        self._mfix.remove_smallest_components()

    def clean(self, max_iters: int = 10, inner_loops: int = 3) -> bool:
        """
        Remove degenerate triangles and self-intersections.

        Iteratively calls :func:`MeshFix.strong_degeneracy_removal` and
        :func:MeshFix.strong_intersection_removal to produce a clean mesh
        without degeneracies and intersections.  The two aforementioned methods
        are called up to max_iter times and each of them is called using
        'inner_loops' as a parameter.  Returns ``True`` only if the mesh could
        be completely cleaned.

        Parameters
        ----------
        max_iters

        """
        return self._mfix.clean(max_iters, inner_loops)

    def degeneracy_removal(self, max_iter: int = 3) -> bool:
        """
        Remove degenerate triangles.


        Parameters
        ----------
        max_iter : int, default: 3
            Maximum number of iterations to perform.

        Returns
        -------
        bool
            ``True`` when successful.

        """
        return self._mfix.strong_degeneracy_removal(max_iter)

    def intersection_removal(self, max_iter: int = 3) -> bool:
        """
        Remove self-intersecting triangles.

        Parameters
        ----------
        max_iter : int, default: 3
            Maximum number of iterations to perform.

        Returns
        -------
        bool
            ``True`` when successful.

        """
        return self._mfix.strong_intersection_removal(max_iter)

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
