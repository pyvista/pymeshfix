"""
Python module to interface with wrapped meshfix

"""
import numpy as np
import ctypes
import warnings
from pymeshfix import _meshfix

try:
    import vtkInterface as vtki
    vtkenabled = True
except BaseException:
    warnings.warn('Unable to import vtkInterface.  Will be unable to plot meshes')
    vtkenabled = False


class MeshFix(object):
    """
    Cleans and tetrahedralize surface meshes using MeshFix

    Parameters
    ----------
    args : vtkInterface.PolyData or (np.ndarray, np.ndarray)
        Either a vtkInterface surface mesh or a nx3 vertex array and nx3 face
        array.

    """

    def __init__(self, *args):
        """ initializes MeshFix """
        if isinstance(args[0], vtki.PolyData):
            mesh = args[0]
            self.v = mesh.points
            self.f = mesh.GetNumpyFaces(force_C_CONTIGUOUS=True)
        elif isinstance(args[0], np.ndarray):
            self.LoadArrays(args[0], args[1])
        else:
            raise Exception('Invalid input')

    def LoadArrays(self, v, f):
        """
        Loads triangular mesh from vertex and face arrays

        Face arrays/lists are v and f.  Both vertex and face arrays should be
        2D arrays with each vertex containing XYZ data and each face containing
        three points
        """
        # Check inputs
        if not isinstance(v, np.ndarray):
            try:
                v = np.asarray(v, np.float)
                if v.ndim != 2 and v.shape[1] != 3:
                    raise Exception(
                        'Invalid vertex format.  Shape should be (npoints, 3)')
            except BaseException:
                raise Exception(
                    'Unable to convert vertex input to valid numpy array')

        if not isinstance(f, np.ndarray):
            try:
                f = np.asarray(f, ctypes.c_int)
                if f.ndim != 2 and f.shape[1] != 3:
                    raise Exception(
                        'Invalid face format.  Shape should be (nfaces, 3)')
            except BaseException:
                raise Exception(
                    'Unable to convert face input to valid numpy array')

        # Store to self
        self.v = v
        self.f = f

    @property
    def mesh(self):
        """ the surface mesh """
        if vtkenabled:
            return vtki.MeshfromVF(self.v, self.f)
        else:
            raise Exception('Cannot generate mesh without vtkInterface.\n' +
                            'Run: pip install vtkInterface')

    def Plot(self, showbound=True):
        """
        Plot the mesh.

        Parameters
        ----------
        showbound : bool, optional
            Shows boundaries.  Default True
        """
        if showbound:
            vtki.PlotBoundaries(self.mesh, showedges=True)
        else:
            self.mesh.Plot(showedges=True)

    def Repair(self, verbose=False, joincomp=False, removeSmallestComponents=True):
        """
        Performs mesh repair using MeshFix's default repair process

        Parameters
        ----------
        verbose : bool, optional
            Enables or disables debug printing.  Disabled by default.

        joincomp : bool, optional
            Attempts to join nearby open components.
        
        removeSmallestComponents : bool, optional
            Remove all but the largest isolated component from the mesh
            before beginning the repair process.  Default True

        Notes
        -----
        Vertex and face arrays are updated inplace.  Access them with:
        meshfix.v
        meshfix.f

        """
        self.v, self.f = _meshfix.CleanFromVF(self.v, self.f, verbose,
                                              joincomp, removeSmallestComponents)

    def Write(self, filename, ftype=None, binary=True):
        """
        Writes a surface mesh to disk.

        Written file may be an ASCII or binary ply, stl, or vtk mesh file.

        Parameters
        ----------
        filename : str
            Filename of mesh to be written.  Filetype is inferred from the
            extension of the filename unless overridden with ftype.  Can be
            one of the following types (.ply, .stl, .vtk)

        ftype : str, optional
            Filetype.  Inferred from filename unless specified with a three
            character string.  Can be one of the following: 'ply',  'stl', or
            'vtk'.

        Notes
        -----
        Binary files write much faster than ASCII.
        """
        if not vtkenabled:
            raise Exception('Cannot save mesh without vtk.  ' +
                            'Please install vtk with python bindings.')

        self.mesh.Write()
