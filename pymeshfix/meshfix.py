"""
Python module to interface with wrapped TetGen C++ code

"""
from pymeshfix import _meshfix
import numpy as np
import ctypes
import warnings

# optional VTK import
try:
    import vtkInterface
    vtkenabled = True
except BaseException:
    warnings.warn('Unable to import vtk.  To plot meshes install vtkInterface')
    vtkenabled = False


class MeshFix(object):
    """
    Class to clean, and tetrahedralize surface meshes using MeshFix

    """

    def __init__(self):
        """ initializes object """
        pass  # nothing needs to be done here yet

    def LoadVF(self, v, f):
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

    def LoadFile(self, filename):
        """
        If vtk is installed, meshes can be loaded directly from file.

        Allowable filetypes: *.ply, *.stl, and *.vtk files

        """
        if not vtkenabled:
            raise Exception(
                'Cannot import mesh from file without vtk installed')

        # Store vertices and faces
        mesh = vtkInterface.PolyData(filename)
        self.LoadMesh(mesh)

    def LoadMesh(self, mesh):
        """
        Loads triangular mesh from a vtk.vtkPolyData object

        """

        # Various load methods depending on input
        if not vtkenabled:
            raise Exception('Cannot import vtk mesh without vtk installed.')
        self.v = mesh.points
        self.f = mesh.GetNumpyFaces(force_C_CONTIGUOUS=True)

    def PlotInput(self, showbound=True):
        """
        Displays input mesh

        Shows boundaries if showbound is enabled
        """

        if not vtkenabled:
            raise Exception('Cannot display mesh without vtk.  ' +
                            'Please install vtk with python bindings.')

        mesh = vtkInterface.MeshfromVF(self.v, self.f)

        if showbound:
            vtkInterface.PlotBoundaries(mesh, showedges=True)
        else:
            mesh.Plot(showedges=True)

    def Repair(self, verbose=True, joincomp=False,
               removeSmallestComponents=True):
        """
        Performs mesh repair using MeshFix's default repair process

        """
        if not hasattr(self, 'v'):
            raise Exception('No mesh loaded')

        self.vclean, self.fclean = _meshfix.CleanFromVF(
            self.v, self.f, verbose, joincomp, removeSmallestComponents)

    def DisplayFixedSurface(self, showbound=True):
        """ Displays input mesh """
        if not vtkenabled:
            raise Exception('Cannot display mesh without vtk.  ' +
                            'Please install vtk with python bindings.')
        mesh = self.GenFixedMesh()
        if showbound:
            vtkInterface.PlotBoundaries(mesh, showedges=True)
        else:
            mesh.Plot(showedges=True)

    def GenFixedMesh(self):
        """
        Generates a vtkPolyData mesh from the cleaned mesh data

        Parameters
        ----------
        None

        Returns
        -------
        fixedmesh : vtk.PolyData
            Repaired mesh
        """
        if not vtkenabled:
            raise Exception('Cannot create mesh without vtk.  ' +
                            'Please install vtk with python bindings.')

        if not hasattr(self, 'vclean'):
            raise Exception('Run "Repair" first')

        self.fixedmesh = vtkInterface.MeshfromVF(self.vclean, self.fclean)
        return self.fixedmesh

    def SaveFixedMesh(self, filename):
        """ Saves mesh from meshfix to file """
        if not vtkenabled:
            raise Exception('Cannot save mesh without vtk.  ' +
                            'Please install vtk with python bindings.')

        # Generate it if it doesn't exist
        if not hasattr(self, 'fixedmesh'):
            self.GenFixedMesh()

        # Save grid
        self.fixedmesh.Write(filename)
