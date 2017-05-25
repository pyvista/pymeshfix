"""
Python module to interface with wrapped TetGen C++ code

"""
# import cython libraries
from pymeshfix import _meshfix

# VTK import
try:
    import vtk
    vtkenabled = True
except:
    vtkenabled = False
    
if vtkenabled:
    import vtkhelper

import numpy as np
import ctypes

class MeshFixClass(object):
    """
    Class to clean, and tetrahedralize surface meshes using MeshFix
    
    """    
    
    def __init__(self):
        """ initializes object """
        pass # nothing needs to be done here yet
    
    
    def LoadVF(self, v, f):
        """
        Loads triangular mesh from vertex and face arrays
        
        Face arrays/lists are v and f.  Both vertex and face arrays should be 
        2D arrays with each vertex containing XYZ data and each face containing
        three points
        """

        # Check inputs
        if type(v) != np.ndarray:
            try:
                v = np.asarray(v, np.float)
                if v.ndim != 2 and v.shape[1] != 3:
                    raise Exception('Invalid vertex format.  Shape should be (npoints, 3)')
            except:
                raise Exception('Unable to convert vertex input to valid numpy array')

        if type(f) != np.ndarray:
            try:
                f = np.asarray(f, ctypes.c_int)
                if f.ndim != 2 and f.shape[1] != 3:
                    raise Exception('Invalid face format.  Shape should be (nfaces, 3)')
            except:
                raise Exception('Unable to convert face input to valid numpy array')
                
        # Store to self
        self.v = v
        self.f = f
        
        
    def LoadFile(self, filename):
        """
        If vtk is installed, meshes can be loaded directly from file.

        Allowable filetypes: *.ply, *.stl, and *.vtk files

        """
        
        # Check to see if vtk exists
        if not vtkenabled:
            raise Exception('Cannot import mesh from file without vtk installed')
            
        # Store vertices and faces
        vtkpoly = vtkhelper.LoadMesh(filename)
        self.v = vtkhelper.GetPoints(vtkpoly)
        self.f = vtkhelper.GetFaces(vtkpoly)
        
        
    def LoadMesh(self, vtkpoly):
        """
        Loads triangular mesh from a vtk.vtkPolyData object
        
        TetGenClass(filename=filename)
        If vtk is installed, meshes can be loaded directly from file.  Accepts:
        *.ply, *.stl, and *.vtk files
        
        """
        
        # Various load methods depending on input
        if not vtkenabled:
            raise Exception('Cannot import vtk mesh without vtk installed.')
        
#        if type(vtkpoly) is vtk.vtkPolyData:
        # Store vertices and faces from mesh internally
        self.v = vtkhelper.GetPoints(vtkpoly)
        self.f = vtkhelper.GetFaces(vtkpoly)
            
#        else:
#            raise Exception('Input must be a vtkPolyData mesh')
        
    
    def DisplayInputSurface(self, showbound=True):
        """
        Displays input mesh 

        Shows boundaries if showbound is enabled        
        """
        
        if not vtkenabled:
            raise Exception('Cannot display mesh without vtk.  '  +\
                            'Please install vtk with python bindings.')
        
        mesh = vtkhelper.MeshfromVF(self.v, self.f, clean=False)

        if showbound:
            vtkhelper.PlotBoundaries(mesh)
        else:
            vtkhelper.Plot(mesh)
        
        
    def Repair(self, verbose=True, joincomp=False):
        """
        Performs mesh repair using MeshFix's default repair process       
        
        """
        if not hasattr(self, 'v'):
            raise Exception('No mesh loaded')
            
        self.vclean, self.fclean = _meshfix.CleanFromVF(self.v, self.f, verbose, joincomp)


    def DisplayFixedSurface(self, showbound=True):
        """ Displays input mesh """
        if not vtkenabled:
            raise Exception('Cannot display mesh without vtk.  '  +\
                            'Please install vtk with python bindings.')
        
        mesh = vtkhelper.MeshfromVF(self.vclean, self.fclean, False)

        if showbound:
            vtkhelper.PlotBoundaries(mesh)
        else:
            vtkhelper.Plot(mesh)


    def GenFixedMesh(self):
        """ Generates a vtkPolyData mesh from the cleaned mesh data """
        if not vtkenabled:
            raise Exception('Cannot display mesh without vtk.  '  +\
                            'Please install vtk with python bindings.')
                            
        if not hasattr(self, 'vclean'):
            raise Exception('Run "Repair" first')
            
        self.fixedmesh = vtkhelper.MeshfromVF(self.vclean, self.fclean)
        

    def SaveFixedMesh(self, filename):
        """ Saves mesh from meshfix to file """
        
        if not vtkenabled:
            raise Exception('Cannot save mesh without vtk.  '  +\
                            'Please install vtk with python bindings.')

        # Generate it if it doesn't exist
        if not hasattr(self, 'fixedmesh'):
            self.GenFixedMesh()
                            
        # Save grid
        vtkhelper.WriteMesh(filename, self.fixedmesh)

    
