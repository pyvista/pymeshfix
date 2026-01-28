# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""
Python/Cython wrapper for MeshFix by Marco Attene
"""
import ctypes
import warnings

from libcpp cimport bool

import numpy as np
cimport numpy as np

ctypedef unsigned short UINT16

""" Wrapped tetgen class """
cdef extern from "meshfix.h" namespace "T_MESH":
    cdef cppclass Basic_TMesh_wrap:
        # Constructor
        Basic_TMesh_wrap()

        # Inputs
        int load(const char*)
        int loadArray(int, double*, int, int*)

        # MeshFix
        int removeSmallestComponents()
        int boundaries()
        int fillSmallBoundaries(int, bool)
        int meshclean(int, int)
        int save(const char*, bool)

        # Select self intersecting triangles
        int selectIntersectingTriangles(UINT16, bool)
        void GetSelected(int*)
#        void IntersectionRemoval()

        # Settings
        void SetVerbose(int)

        # Outputs
        int ReturnTotalPoints()
        int ReturnTotalFaces()
        void PopArrays(double*, int*)

        # MISC
        void Join()


cdef class PyTMesh:
    """Cython class to interface with C++ Basic_TMesh object

    MeshFix V2.0 - by Marco Attene If MeshFix is used for research
    purposes, please cite the following paper:

    M. Attene.  A lightweight approach to repairing digitized polygon
    meshes.  The Visual Computer, 2010. (c) Springer.

    Examples
    --------
    Create an instance of TMesh.

    >>> from pymeshfix import _meshfix
    >>> tin = _meshfix.PyTMesh()

    Load a file.

    >>> tin.load_file(infile)

    Load from arrays.

    >>> tin.load_array(v, f)

    Attempt to join nearby components.

    >>> tin.join_closest_components()

    Fill holes.

    >>> tin.fill_small_boundaries()
    >>> print('There are {:d} boundaries'.format(tin.boundaries())

    Clean and remove self intersections.

    >>> tin.clean(max_iters=10, inner_loops=3)

    Check mesh for holes again.

    >>> print('There are {:d} boundaries'.format(tin.boundaries())

    Output mesh.

    >>> tin.save_file(outfile)

    return numpy arrays

    >>> vclean, fclean = tin.return_arrays()

    """

    cdef Basic_TMesh_wrap c_tmesh  # hold a C++ instance which we're wrapping

    def __cinit__(self, verbose=1):
        """ Create TMesh object """
        self.c_tmesh = Basic_TMesh_wrap()

        # Enable/Disable printed progress
        quiet = 0 if verbose else 1
        self.c_tmesh.SetVerbose(quiet)

    def load_file(self, filename):
        """
        Loads mesh from file

        Currently, the following file formats are supported:
        Open Inventor (IV), VRML 1.0 and 2.0 (WRL), Object File Format (OFF),
        IMATI Ver-Tri (VER, TRI), PLY, OBJ, STL.

        The loader automatically reconstructs a manifold triangle connectivity

        Examples
        --------
        >>> from pymeshfix import _meshfix
        >>> tin = _meshfix.PyTMesh()
        >>> tin.LoadFile('file.ply')

        """
        if self.n_points:
            raise RuntimeError('Cannot load a new file once initialized')

        # Initializes triangulation
        py_byte_string = filename.encode('UTF-8')
        cdef char* cstring = py_byte_string
        result = self.c_tmesh.load(cstring);
        if result:
            raise IOError('MeshFix is unable to open %s' % filename)

    def save_file(self, filename, back_approx=False):
        """Save cleaned mesh to file

        The file format is deduced from one of the following filename
        extensions:

            - ``"wrl"`` - vrml 1.0
            - ``"iv"`` - OpenInventor
            - ``"off"`` - Object file format
            - ``"ply"`` - PLY format
            - ``"tri"`` - IMATI Ver-Tri

        If 'back_approx' is set to True, vertex coordinates are approximated
        to reflect the limited precision of floating point
        representation in ASCII files. This should be used when
        coherence is necessary between in-memory and saved data.
        A non-zero return value is returned if errors occur.

        Examples
        --------
        >>> tin.save_file(outfile)

        """

        # Convert filename to c string and save
        py_byte_string = filename.encode('UTF-8')
        cdef char* cstring = py_byte_string
        result = self.c_tmesh.save(cstring, back_approx)

        if result:
            raise IOError('MeshFix is unable to save mesh to %s' % filename)

    @property
    def n_points(self):
        """Number of points in the mesh"""
        cdef int n_points = self.c_tmesh.ReturnTotalPoints()
        return n_points

    def load_array(self, v, f):
        """Load points from numpy vertices and faces arrays.

        The loader automatically reconstructs a manifold triangle connectivity.

        Parameters
        ----------
        v : np.ndarray
            Numpy array containing vertices.  Sized n x 3

        f : np.ndarray
            Numpy array containing mesh faces.  Sized n x 3

        Examples
        --------
        >>> tin.load_array(v, f)

        """
        if self.n_points:
            raise RuntimeError('Cannot load new arrays once initialized')

        v = np.ascontiguousarray(v, dtype=np.float64)

        # Ensure inputs are of the right type
        f = np.ascontiguousarray(f, dtype=ctypes.c_int)
        if f.ndim != 2 or f.shape[1] != 3:
            raise ValueError(
                f'Face array must be 2D with three columns, got {f.shape}')

        cdef int nv = v.shape[0]
        cdef double [::1] points = v.ravel()

        cdef int nt = f.shape[0]
        cdef int [::1] faces = f.ravel()

        # Load to C object
        self.c_tmesh.loadArray(nv, &points[0], nt, &faces[0])

    def clean(self, int max_iters=10, inner_loops=3):
        """Remove self-intersections and degenerate faces.

        Iteratively call strongDegeneracyRemoval and
        strongIntersectionRemoval to produce an eventually clean mesh
        without degeneracies and intersections.  The two
        aforementioned methods are called up to max_iter times and
        each of them is called using 'inner_loops' as a parameter.
        Returns true only if the mesh could be completely cleaned.

        Examples
        --------
        >>> tin.clean(max_iters=10, inner_loops=3)

        """
        self.c_tmesh.meshclean(max_iters, inner_loops)

    def boundaries(self):
        """Get the number of boundary loops of the triangle mesh"""
        return self.c_tmesh.boundaries()

    def remove_smallest_components(self):
        """Remove smallest components"""
        return self.c_tmesh.removeSmallestComponents()

    def fill_small_boundaries(self, nbe=0, refine=True):
        """Fill small boundaries.

        Fills all the holes having less than ``nbe`` boundary
        edges. If ``refine`` is true, adds inner vertices to reproduce
        the sampling density of the surroundings. Returns number of
        holes patched.  If 'nbe' is 0 (default), all the holes are
        patched.

        Examples
        --------
        Fill all holes.

        >>> tin.fill_small_boundaries()

        """
        return self.c_tmesh.fillSmallBoundaries(nbe, refine)

    def return_arrays(self):
        """Return vertex and face arrays of the mesh.

        Returns
        -------
        numpy.ndarray
            Points array.

        numpy.ndarray
            Faces array.

        Examples
        --------
        >>> points, faces = tin.return_arrays()
        """

        # Size point array
        cdef int npoints = self.c_tmesh.ReturnTotalPoints()
        cdef double [::1] points = np.empty(npoints*3)

        # Size face array
        cdef int nfaces = self.c_tmesh.ReturnTotalFaces()
        cdef int [::1] faces = np.empty(nfaces*3, ctypes.c_int)

        # Populate points array
        self.c_tmesh.PopArrays(&points[0], &faces[0])

        v = np.asarray(points).reshape((-1, 3))
        f = np.asarray(faces).reshape((-1, 3))

        return v, f

    def join_closest_components(self):
        """Attempt to join nearby open components.

        Should be run before mesh repair.

        Examples
        --------
        >>> tin.join_closest_components()

        """
        self.c_tmesh.Join()

    def select_intersecting_triangles(self, UINT16 tris_per_cell=50,
                                      bool justproper=False):
        """Selects all intersecting triangles.

        Selects all the triangles that improperly intersect other
        parts of the mesh and return their number. The parameter
        'tris_per_cell' determines the depth of the recursive space
        subdivision used to keep the complexity under a reasonable
        threshold. The default value is safe in most cases.

        If ``justproper`` is true, coincident edges and vertices are not
        regarded as intersections even if they are not common
        subsimplexes.

        Returns
        -------
        numpy.ndarray
            Array of face indices.

        Examples
        --------
        >>> faces = tin.select_intersecting_triangles()

        """
        # Returns the number of intersecting triangles
        its = self.c_tmesh.selectIntersectingTriangles(tris_per_cell, justproper)

        # Create a face array and populate it with the intersecting faces
        cdef int [::1] faces = np.empty(its, ctypes.c_int)
        self.c_tmesh.GetSelected(&faces[0])

        return np.asarray(faces)

#    def IntersectionRemoval(self):
#        """ Remove intersections """
#        self.c_tmesh.IntersectionRemoval()


def clean_from_file(infile, outfile, verbose=False, joincomp=False):
    """Performs default cleaning procedure on an input file and writes to disk.

    Performs default cleaning procedure on input file and writes the
    repaired mesh to disk.  Output file will be a single manifold mesh.

    Parameters
    ----------
    infile : str
        Filename of input file to read.  Must be either a .stl, .off or
        .ply file.

    outfile : str
        Filename of input file to write.  Must be either a .stl, .off or
        .ply file.

    verbose : bool, optional
        Prints progress to stdout.  Default ``True``.

    joincomp : bool, optional
        Attempt to join nearby open components.  Default ``False``.

    Examples
    --------
    Clean a mesh without using pyvista or vtk.

    >>> import pymeshfix
    >>> pymeshfix.clean_from_file('inmesh.ply', 'outmesh.ply')

    """
    # Create mesh object and load from file
    tin = PyTMesh(verbose)
    tin.load_file(infile)
    if joincomp:
        tin.join_closest_components()

    repair(tin, verbose, joincomp)

    # Save to file
    if verbose:
        print('Saving repaired mesh to %s' % outfile)
    tin.save_file(outfile)


def clean_from_arrays(v, f, verbose=False, joincomp=False,
                      remove_smallest_components=True):
    """Perform default cleaning procedure on vertex and face arrays.

    Returns cleaned vertex and face arrays

    Parameters
    ----------
    v : numpy.ndarray
        Numpy n x 3 array of vertices

    f : numpy.ndarray
        Numpy n x 3 array of faces.

    verbose : bool, optional
        Prints progress to stdout.  Default ``True``.

    joincomp : bool, optional
        Attempts to join nearby open components.  Default ``False``.

    remove_smallest_components : bool, optional
        Remove all but the largest isolated component from the mesh
        before beginning the repair process.  Default ``True``.

    Returns
    -------
    numpy.ndarray
        Points array.

    numpy.ndarray
        Faces array.

    Examples
    --------
    >>> import pymeshfix
    >>> import numpy as np
    >>> points = np.load('points.npy')
    >>> faces = np.load('faces.npy')
    >>> clean_points, clean_faces = pymeshfix.clean_from_arrays(points, faces)

    """
    # Create mesh object and load from file
    tin = PyTMesh(verbose)
    tin.load_array(v, f)

    # repari and return vertex and face arrays
    repair(tin, verbose, joincomp, remove_smallest_components)
    return tin.return_arrays()


def repair(tin, verbose=False, joincomp=True, remove_smallest_components=True):
    """
    Performs mesh repair using default cleaning procedure using a tin object.

    Internal function.  Use ``clean_from_file`` or CleanFromVF.
    """

    # Keep only the largest component (i.e. with most triangles)
    if remove_smallest_components:
        sc = tin.remove_smallest_components()
        if sc and verbose:
            print('Removed %d small components' % sc)

    # join closest components
    if joincomp:
        tin.join_closest_components()

    if tin.boundaries():
        if verbose:
            print('Patching holes...')
        holespatched = tin.fill_small_boundaries()
        if verbose:
            print('Patched %d holes' % holespatched)

    # Perform mesh cleaning
    if verbose:
        print('Fixing degeneracies and intersections')

    tin.boundaries()
    result = tin.clean()

    # Check boundaries again
    if tin.boundaries():
        if verbose:
            print('Patching holes...')
        holespatched = tin.fill_small_boundaries()
        if verbose:
            print('Patched %d holes' % holespatched)

        if verbose:
            print('Performing final check...')
        result = tin.clean()

    if result:
        warnings.warn('MeshFix could not fix everything')
