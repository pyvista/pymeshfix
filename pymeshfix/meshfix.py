"""Python module to interface with wrapped meshfix."""

import ctypes

import numpy as np

from pymeshfix import _meshfix

try:
    import pyvista as pv

    PV_INSTALLED = True
except ImportError:
    PV_INSTALLED = False


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
        if isinstance(args[0], np.ndarray):
            self.load_arrays(args[0], args[1])
        elif PV_INSTALLED:
            if isinstance(args[0], pv.PolyData):
                mesh = pv.wrap(args[0])
                self.v = mesh.points

                # check if triangular mesh
                faces = mesh.faces
                if not mesh.is_all_triangles:
                    tri_mesh = mesh.triangulate()
                    faces = tri_mesh.faces

                self.f = np.ascontiguousarray(faces.reshape(-1, 4)[:, 1:])

        else:
            raise TypeError("Invalid input. Please load a surface mesh or face and vertex arrays")

    def load_arrays(self, v, f):
        """Load triangular mesh from vertex and face numpy arrays.

        Both vertex and face arrays should be 2D arrays with each
        vertex containing XYZ data and each face containing three
        points.

        Parameters
        ----------
        v : np.ndarray
            n x 3 vertex array.

        f : np.ndarray
            n x 3 face array.

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
                v = np.asarray(v, np.float64)
                if v.ndim != 2 and v.shape[1] != 3:
                    raise ValueError(
                        f"Invalid vertex shape {v.shape}.  Shape should be (npoints, 3)"
                    )
            except BaseException:
                raise ValueError("Unable to convert vertex input to valid numpy array.")

        if not isinstance(f, np.ndarray):
            try:
                f = np.asarray(f, ctypes.c_int)
                if f.ndim != 2 and f.shape[1] != 3:
                    raise ValueError(
                        f"Invalid vertex shape {v.shape}.  Shape should be (npoints, 3)"
                    )
            except BaseException:
                raise ValueError("Unable to convert face input to valid numpy array.")

        self.v = v
        self.f = f

    @property
    def mesh(self):
        """Return the surface mesh.

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
        if not PV_INSTALLED:
            raise ImportError(
                "Please install pyvista for this feature with:\n\n    pip install pyvista"
            )
        triangles = np.empty((self.f.shape[0], 4), dtype=pv.ID_TYPE)
        triangles[:, -3:] = self.f
        triangles[:, 0] = 3
        return pv.PolyData(self.v, triangles, deep=False)

    def extract_holes(self):
        """Extract the boundaries of the holes in this mesh to a new PyVista mesh of lines."""
        return self.mesh.extract_feature_edges(
            boundary_edges=True, feature_edges=False, manifold_edges=False
        )

    @property
    def points(self):
        """Return the points of the mesh.

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
    def faces(self):
        """Return the indices of the faces of the mesh.

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

    def plot(self, show_holes=True, **kwargs):
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
        if not PV_INSTALLED:
            raise ImportError(
                "Please install pyvista for this feature with:\n\n    pip install pyvista"
            )

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
                plotter.add_legend()
            return plotter.show(screenshot=screenshot)

        return self.mesh.plot(**kwargs)

    def repair(self, verbose=False, joincomp=False, remove_smallest_components=True):
        """Perform mesh repair using MeshFix's default repair process.

        Parameters
        ----------
        verbose : bool, default: False
            Enables or disables debug printing.

        joincomp : bool, default: False
            Attempts to join nearby open components.

        remove_smallest_components : bool, default: True
            Remove all but the largest isolated component from the
            mesh before beginning the repair process.

        Notes
        -----
        Vertex and face arrays are updated inplace.  Access them with:

        * :attr:`Meshfix.points`
        * :attr:`Meshfix.faces`

        Examples
        --------
        Repair using the verbose option.

        >>> from pyvista import examples
        >>> from pymeshfix import MeshFix
        >>> mesh = examples.download_bunny()
        >>> mfix = MeshFix(mesh)
        >>> mfix.plot(show_holes=True)

        """
        assert self.f.shape[1] == 3, "Face array must contain three columns"
        assert self.f.ndim == 2, "Face array must be 2D"
        self.v, self.f = _meshfix.clean_from_arrays(
            self.v, self.f, verbose, joincomp, remove_smallest_components
        )

    def save(self, filename, binary=True):
        """Write a surface mesh to disk.

        Written file may be in a ASCII or binary PLY, STL, or VTK format.

        This is a a simple wrapper for :pyvista:`pyvista.PolyData.save`.

        Parameters
        ----------
        filename : str
            Filename of mesh to be written.  Filetype is inferred from
            the extension of the filename unless overridden with
            ftype.  Can be one of the following types (.ply, .stl,
            .vtk)

        binary: bool, default: True
            Filetype.  Inferred from filename unless specified with a
            three character string.  Can be one of the following:
            ``'ply'``, ``'stl'``, or ``'vtk'``.

        Notes
        -----
        Binary files write much faster than ASCII.

        """
        return self.mesh.save(filename, binary)
