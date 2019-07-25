"""Python module to interface with wrapped meshfix
"""
import ctypes
import warnings
import numpy as np

from pymeshfix import _meshfix
import pyvista as pv


class MeshFix(object):
    """Cleans and tetrahedralize surface meshes using MeshFix

    Parameters
    ----------
    args : pyvista.PolyData or (np.ndarray, np.ndarray)
        Either a pyvista surface mesh :class:`pyvista.PolyData` or a (n x 3)
        vertex array and (n x 3) face array (indices of the triangles).

    """

    def __init__(self, *args):
        """Initialize MeshFix """
        if isinstance(args[0], pv.PolyData):
            mesh = pv.wrap(args[0])
            self.v = mesh.points

            # check if triangular mesh
            faces = mesh.faces
            if faces.size % 4:
                tri_mesh = mesh.tri_filter()
                faces = tri_mesh.faces

            self.f = np.ascontiguousarray(faces.reshape(-1 , 4)[:, 1:])

        elif isinstance(args[0], np.ndarray):
            self.load_arrays(args[0], args[1])

        else:
            raise Exception('Invalid input.  Please load a surface mesh or' +
                            ' face and vertex arrays')

    def load_arrays(self, v, f):
        """Loads triangular mesh from vertex and face numpy arrays.

        Both vertex and face arrays should be 2D arrays with each
        vertex containing XYZ data and each face containing three
        points.

        Parameters
        ----------
        v : np.ndarray
            n x 3 vertex array.

        f : np.ndarray
            n x 3 face array.
        """
        # Check inputs
        if not isinstance(v, np.ndarray):
            try:
                v = np.asarray(v, np.float)
                if v.ndim != 2 and v.shape[1] != 3:
                    raise Exception('Invalid vertex format.  Shape ' +
                                    'should be (npoints, 3)')
            except BaseException:
                raise Exception(
                    'Unable to convert vertex input to valid numpy array')

        if not isinstance(f, np.ndarray):
            try:
                f = np.asarray(f, ctypes.c_int)
                if f.ndim != 2 and f.shape[1] != 3:
                    raise Exception('Invalid face format.  ' +
                                    'Shape should be (nfaces, 3)')
            except BaseException:
                raise Exception('Unable to convert face input to valid' +
                                ' numpy array')

        self.v = v
        self.f = f

    @property
    def mesh(self):
        """Return the surface mesh"""
        triangles = np.empty((self.f.shape[0], 4))
        triangles[:, -3:] = self.f
        triangles[:, 0] = 3
        return pv.PolyData(self.v, triangles, deep=False)

    def extract_holes(self):
        """Extract the boundaries of the holes in this mesh to a new PyVista
        mesh of lines.
        """
        return self.mesh.extract_edges(boundary_edges=True,
                                       feature_edges=False,
                                       manifold_edges=False)

    def plot(self, show_holes=True, **kwargs):
        """Plot the mesh.

        Parameters
        ----------
        show_holes : bool, optional
            Shows boundaries.  Default True

        **kwargs : keyword arguments
            Additional keyword arguments.

        """
        if show_holes:
            edges = self.extract_holes()

            plotter = pv.Plotter()
            plotter.add_mesh(self.mesh, label='mesh')
            plotter.add_mesh(edges, 'r', label='edges')
            plotter.show()

        else:
            self.mesh.plot(show_edges=True)

    def repair(self, verbose=False, joincomp=False,
               remove_smallest_components=True):
        """Performs mesh repair using MeshFix's default repair
        process.

        Parameters
        ----------
        verbose : bool, optional
            Enables or disables debug printing.  Disabled by default.

        joincomp : bool, optional
            Attempts to join nearby open components.

        remove_smallest_components : bool, optional
            Remove all but the largest isolated component from the
            mesh before beginning the repair process.  Default True

        Notes
        -----
        Vertex and face arrays are updated inplace.  Access them with:
        meshfix.v
        meshfix.f
        """
        assert self.f.shape[1] == 3, 'Face array must contain three columns'
        assert self.f.ndim == 2, 'Face array must be 2D'
        self.v, self.f = _meshfix.clean_from_arrays(self.v, self.f,
                                                    verbose, joincomp,
                                                    remove_smallest_components)

    def save(self, filename, binary=True):
        """Writes a surface mesh to disk.

        Written file may be an ASCII or binary ply, stl, or vtk mesh
        file.

        This is a a simple wrapper for PyVista's save method

        Parameters
        ----------
        filename : str
            Filename of mesh to be written.  Filetype is inferred from
            the extension of the filename unless overridden with
            ftype.  Can be one of the following types (.ply, .stl,
            .vtk)

        ftype : str, optional
            Filetype.  Inferred from filename unless specified with a
            three character string.  Can be one of the following:
            'ply', 'stl', or 'vtk'.

        Notes
        -----
        Binary files write much faster than ASCII.
        """
        return self.mesh.save(filename, binary)

    def write(self, filename, binary=True):
        """ DEPRECATED """
        warnings.warn('`.write` is deprecated. Use `.save` instead.', RuntimeWarning)
        return self.save(filename, binary=binary)
