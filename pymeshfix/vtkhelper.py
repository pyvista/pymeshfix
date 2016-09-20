"""
This module provides functions to support a vtk/numpy interface
"""
import os

import vtk
import numpy as np
import ctypes

# Determine if using vtk > 5
new_vtk = vtk.vtkVersion().GetVTKMajorVersion() > 5
from vtk.util import numpy_support as VN


def SetVTKInput(obj, inp):
    """
    Accounts for version discrepancy between VTK versions in input methods
    """
    
    if new_vtk:
        obj.SetInputData(inp)
    else:
        obj.SetInput(inp)
        
        
def MakeuGrid(offset, cells, cell_type, nodes):
    """ Create VTK unstructured grid """
    
    # Check inputs (necessary since offset and cells can int32)    
    if offset.dtype != 'int64':
        offset = offset.astype(np.int64)
    
    if cells.dtype != 'int64':
        cells = cells.astype(np.int64)
    
    # Get number of cells
    ncells = len(cell_type)
    
    # Convert to vtk arrays
    cell_type = VN.numpy_to_vtk(cell_type, deep=True)
    offset = VN.numpy_to_vtkIdTypeArray(offset, deep=True)
    
    vtkcells = vtk.vtkCellArray()
    vtkcells.SetCells(ncells, VN.numpy_to_vtkIdTypeArray(cells, deep=True))
    
    # Convert points to vtkfloat object
    vtkArray = VN.numpy_to_vtk(np.ascontiguousarray(nodes), deep=True)
    points = vtk.vtkPoints()
    points.SetData(vtkArray)
    
    # Create unstructured grid
    uGrid = vtk.vtkUnstructuredGrid()
    uGrid.SetPoints(points)
    uGrid.SetCells(cell_type, offset, vtkcells)
    
    return uGrid        
        
        
def MeshfromVF(points, triangles, clean=True):
    """ Generates mesh from points and triangles """
    
    if triangles.shape[1] == 3:
        triangles = np.hstack((3*np.ones((triangles.shape[0], 1), np.int),
                               triangles))
    
    # Data checking
    if not points.flags['C_CONTIGUOUS']:
        points = np.ascontiguousarray(points)
        
    if not triangles.flags['C_CONTIGUOUS'] or triangles.dtype != 'int64':
        triangles = np.ascontiguousarray(triangles, 'int64')

    # Convert to vtk objects
    vtkpoints = vtk.vtkPoints()
    vtkpoints.SetData(VN.numpy_to_vtk(points, deep=True))
    
    # Convert to a vtk array
    vtkcells = vtk.vtkCellArray()
    vtkcells.SetCells(triangles.shape[0], VN.numpy_to_vtkIdTypeArray(triangles,
                                                                     deep=True))
    
    # Create polydata object
    mesh = vtk.vtkPolyData()
    mesh.SetPoints(vtkpoints)
    mesh.SetPolys(vtkcells)
    
    # return cleaned mesh
    if clean:
        return CleanMesh(mesh)    
    else:
        return mesh
        
        
def CleanMesh(mesh, return_indices=False):
    """ Cleans mesh and returns original indices """
    
    if return_indices:
        npoints = mesh.GetNumberOfPoints()
        AddPointScalars(mesh, np.arange(npoints), 'cleanIDX', False)

    clean = vtk.vtkCleanPolyData()
    clean.ConvertPolysToLinesOff()
    clean.ConvertLinesToPointsOff()
    clean.ConvertStripsToPolysOff()
    SetVTKInput(clean, mesh)
    clean.Update()
    cleanmesh = clean.GetOutput()
    
    if return_indices:
        origID = VN.vtk_to_numpy(cleanmesh.GetPointData().GetArray('cleanIDX'))
        
        # remove last array
        narr = cleanmesh.GetPointData().GetNumberOfArrays()
        cleanmesh.GetPointData().RemoveArray(narr - 1)
        
        return cleanmesh, origID
        
    else:
        return cleanmesh
        

def GetPoints(mesh, datatype=[]):
    """ returns points from a vtk mesh as numpy array """
    points = VN.vtk_to_numpy(mesh.GetPoints().GetData())
    
    if datatype:
        if points.dtype != datatype:
            return points.astype(datatype)
    
    return points


def GetFaces(mesh):
    """
    Returns points from a polydata polydata object and return as a numpy int array
    
    """
    faces = VN.vtk_to_numpy(mesh.GetPolys().GetData()).reshape(-1, 4)[:, 1:]
    
    return np.ascontiguousarray(faces, ctypes.c_int)


def LoadMesh(filename):
    """ Reads mesh from file """

    # Check if file exists
    if not os.path.isfile(filename):
        raise Exception('File {:s} does not exist!'.format(filename))

    # Get extension
    fext = filename[-3:].lower()

    # Select reader
    if fext == 'ply':
        reader = vtk.vtkPLYReader()
        
    elif fext == 'stl':
        reader = vtk.vtkSTLReader()
        
    elif fext == 'vtk':
        reader = vtk.vtkXMLPolyDataReader()
        
    else:
        raise Exception('Can only import *.ply, *.stl, or *.vtk files!')
    
    # Load file
    reader.SetFileName(filename) 
    reader.Update()
    
    return reader.GetOutput()


def CopyGrid(grid):
    """ Copies a vtk structured, unstructured, or polydata object """
    if isinstance(grid, vtk.vtkUnstructuredGrid):
        gridcopy = vtk.vtkUnstructuredGrid()
    elif isinstance(grid, vtk.vtkStructuredGrid):
        gridcopy = vtk.vtkStructuredGrid()
    elif isinstance(grid, vtk.vtkPolyData):
        gridcopy = vtk.vtkPolyData()
        
    gridcopy.DeepCopy(grid)
    return gridcopy
    
    
def MakevtkPoints(numpypts):
    """ Convert numpy points to vtkPoints """
    vtkArray = VN.numpy_to_vtk(np.ascontiguousarray(numpypts), deep=True)
    vpts = vtk.vtkPoints()
    vpts.SetData(vtkArray)
    return vpts
    
    
def AddPointScalars(mesh, scalars, name, setactive=True):
    """
    Adds point scalars to a VTK object or structured/unstructured grid """
    vtkarr = VN.numpy_to_vtk(np.ascontiguousarray(scalars), deep=True)
    vtkarr.SetName(name)
    mesh.GetPointData().AddArray(vtkarr)
    if setactive:
        mesh.GetPointData().SetActiveScalars(name)
    
    
def AddCellScalars(grid, scalars, name):
    """ Adds cell scalars to uGrid """
    vtkarr = VN.numpy_to_vtk(np.ascontiguousarray(scalars), deep=True)
    vtkarr.SetName(name)
    grid.GetCellData().AddArray(vtkarr)
    grid.GetCellData().SetActiveScalars(name)


###############################################################################
# Plotting
###############################################################################
class PlotClass(object):
    """ Simple interface to VTK's underlying ploting """
    
    def __init__(self):

        # Add FEM Actor to renderer window
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.3, 0.3, 0.3)
        
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)
        
        # Allow user to interact
        istyle = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(istyle)


    def AddMesh(self, meshin, color=[1, 1, 1], style='', scalars=[], name='',
                rng=[], stitle='', showedges=True, psize=5, opacity=1,
                linethick=[]):
        """ Adds an actor to the renderwindow """
                
        # Create mapper
        mapper = vtk.vtkDataSetMapper()
                
        # Add scalars if they exist
        isscalars = False
        nscalars = len(scalars)
        if nscalars == meshin.GetNumberOfPoints():
            mesh = CopyGrid(meshin)
            AddPointScalars(mesh, scalars, name)
            isscalars = True
            mapper.SetScalarModeToUsePointData()
            

        elif nscalars == meshin.GetNumberOfCells():
            mesh = CopyGrid(meshin)
            AddCellScalars(mesh, scalars, name)
            isscalars = True
            mapper.SetScalarModeToUseCellData()
            
        else:
            mesh = meshin
                    
        # Set scalar range
        if isscalars:
            if not rng:
                rng = [np.min(scalars), np.max(scalars)]
            mapper.SetScalarRange(rng[0], rng[1])
        
        # Set Scalar
        SetVTKInput(mapper, mesh)
        
        # Create Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        if style == 'wireframe':
            actor.GetProperty().SetRepresentationToWireframe()
        elif style == 'points':
            actor.GetProperty().SetRepresentationToPoints()
            actor.GetProperty().SetPointSize(psize)
        else:
            actor.GetProperty().SetRepresentationToSurface()
            
        if showedges:
            actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().LightingOff()
        
        if style == 'wireframe' and linethick:
            actor.GetProperty().SetLineWidth(linethick) 

        
        # Add to renderer
        self.ren.AddActor(actor)
        
        # Add scalar bar
        if stitle:
            scalarBar = vtk.vtkScalarBarActor()
            scalarBar.SetLookupTable(mapper.GetLookupTable())
            scalarBar.SetTitle(stitle)
            scalarBar.SetNumberOfLabels(5)    
            self.ren.AddActor(scalarBar)


    def AddLines(self, lines, color=[1, 1, 1], width=5):
        """ Adds an actor to the renderwindow """
                
        # Create mapper and add lines
        mapper = vtk.vtkDataSetMapper()
        SetVTKInput(mapper, lines)
        
        # Create Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(width); 
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().LightingOff()
        
        # Add to renderer
        self.ren.AddActor(actor)
        

    def AddPoints(self, points, color=[1, 1, 1], psize=5):
        
        # Convert to points actor if points is a numpy array
        if type(points) == np.ndarray:
            npoints = points.shape[0]
            
            # Make VTK cells array
            cells = np.hstack((np.ones((npoints, 1)), 
                               np.arange(npoints).reshape(-1, 1)))
            cells = np.ascontiguousarray(cells, dtype=np.int64)
            vtkcells = vtk.vtkCellArray()
            vtkcells.SetCells(npoints, VN.numpy_to_vtkIdTypeArray(cells, deep=True))
            
            # Convert points to vtk object
            vtkPoints = MakevtkPoints(points)
            
            # Create polydata
            pdata = vtk.vtkPolyData()
            pdata.SetPoints(vtkPoints)
            pdata.SetVerts(vtkcells)
            
        # Create mapper and add lines
        mapper = vtk.vtkDataSetMapper()
        SetVTKInput(mapper, pdata)
        
        # Create Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(psize); 
        actor.GetProperty().SetColor(color)
        actor.GetProperty().LightingOff()
        
        self.ren.AddActor(actor)
                
        
    def GetCameraPosition(self):
        """ Returns camera position of active render window """
        camera = self.ren.GetActiveCamera()
        pos = camera.GetPosition()
        fpt = camera.GetFocalPoint()
        vup = camera.GetViewUp()
        return [pos, fpt, vup]
        

    def SetCameraPosition(self, cameraloc):
        """ Set camera position of active render window """
        camera = self.ren.GetActiveCamera()
        camera.SetPosition(cameraloc[0])
        camera.SetFocalPoint(cameraloc[1]) 
        camera.SetViewUp(cameraloc[2])        
        

    def SetBackground(self, bcolor):
        """ Sets background color """
        self.ren.SetBackground(bcolor)
        
        
    def AddLegend(self, entries, bcolor=[0.5, 0.5, 0.5], border=False):
        """
        Adds a legend to render window.  Entries must be a list containing
        one string and color entry for each item
        """
        
        legend = vtk.vtkLegendBoxActor()
        legend.SetNumberOfEntries(len(entries))
        
        c = 0
        nulldata = vtk.vtkPolyData()
        for entry in entries:
            legend.SetEntry(c, nulldata, entry[0], entry[1])
            c += 1
        
        legend.UseBackgroundOn()
        legend.SetBackgroundColor(bcolor)
        if border:
            legend.BorderOn()
        else:
            legend.BorderOff()
        
        # Add to renderer
        self.ren.AddActor(legend)
        
        
    def Plot(self, title=''):
        """ Renders """
        if title:
            self.renWin.SetWindowName(title)
            
        # Render
        self.iren.Initialize()
        self.renWin.Render()
        self.iren.Start()
        
        
    def AddActor(self, actor):
        """ Adds actor to render window """
        self.ren.AddActor(actor)
        
        
    def AddAxes(self):
        """ Add axes widget """
        axes = vtk.vtkAxesActor()
        widget = vtk.vtkOrientationMarkerWidget()
        widget.SetOrientationMarker(axes)
        widget.SetInteractor(self.iren)
        widget.SetViewport(0.0, 0.0, 0.4, 0.4)
        widget.SetEnabled(1)
        widget.InteractiveOn()
        

def CreateArrowsActor(pdata):
    """ Creates an actor composed of arrows """
    
    # Create arrow object
    arrow = vtk.vtkArrowSource()
    arrow.Update()
    glyph3D = vtk.vtkGlyph3D()
    if new_vtk:
        glyph3D.SetSourceData(arrow.GetOutput())
        glyph3D.SetInputData(pdata)
    else:
        glyph3D.SetSource(arrow.GetOutput())
        glyph3D.SetInput(pdata)
    glyph3D.SetVectorModeToUseVector()
    glyph3D.Update()
    
    # Create mapper    
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())
    
    # Create actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().LightingOff()

    return actor
    
        
def PlotPoly(mesh, representation='surface', color=[1, 1, 1]):
    """ Plots vtk unstructured grid or poly object """
    pobj = PlotClass()
    pobj.AddMesh(mesh, color, style=representation)
    pobj.Plot()
    del pobj


def Plot(mesh, representation='surface', color=[1, 1, 1]):
    """ calls PlotPoly """
    PlotPoly(mesh, representation, [1, 1, 1])
    
    
def PlotBoundaries(mesh):
    """ Plots boundaries of a mesh """
    
    # Determine boundary edges
    featureEdges = vtk.vtkFeatureEdges()
    SetVTKInput(featureEdges, mesh)
    featureEdges.FeatureEdgesOff()
    featureEdges.BoundaryEdgesOn()
    featureEdges.NonManifoldEdgesOff()
    featureEdges.ManifoldEdgesOff()
    
    edgeMapper = vtk.vtkPolyDataMapper();
    edgeMapper.SetInputConnection(featureEdges.GetOutputPort());
    
    # Create edge actor
    edgeActor = vtk.vtkActor();
    edgeActor.GetProperty().SetLineWidth(5);
    edgeActor.SetMapper(edgeMapper)

    # Render
    plobj = PlotClass()
    plobj.AddMesh(mesh)
    plobj.AddActor(edgeActor)
#    plobj.AddLegend([
#                     ['Mesh',  [1, 1, 1]],
#                     ['Holes', [1, 0, 0]]
#                    ])
    plobj.Plot('Plotting Degenerates Features'); del plobj
    
    
def WriteGrid(filename, grid):
    """ Writes unstructured grid to file """
    # Create VTK writer
    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName(filename)
    SetVTKInput(writer, grid)
    writer.Write()
    
    
def WriteMesh(filename, mesh, binary=True):
    """ Writes a VTK mesh to one of the following formats:
        ply, stl, vtk
    """
    
    # Get extention
    ftype = filename[-3:]
    
    # Get filetype
    if ftype == 'ply':
        writer = vtk.vtkPLYWriter()
    elif ftype == 'stl':
        writer = vtk.vtkSTLWriter()
    elif ftype == 'vtk':
        writer = vtk.vtkPolyDataWriter()
    else:
        raise Exception('Unknown file type')
        
    # Write
    writer.SetFileName(filename)
    SetVTKInput(writer, mesh)
    if binary:
        writer.SetFileTypeToBinary()
    else:
        writer.SetFileTypeToASCII()
    writer.Write()
