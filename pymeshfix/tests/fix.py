""" Demonstrates mesh repair on the standford bunny mesh """
from os.path import dirname, join, realpath
# from pymeshfix import _meshfix
import pymeshfix

# get location of the example mesh
pth = dirname(realpath(__file__))
filename = join(pth, 'StanfordBunny.ply')


def Native():
    """ Repair Stanford Bunny Mesh """
    # get location of this file
    pymeshfix._meshfix.CleanFromFile(filename, 'repaired.ply')


def WithVTK():
    """ Tests VTK interface and mesh repair of Stanford Bunny Mesh """
    try:
        import vtkInterface
    except:
        raise Exception('Install vtkInterface to use this feature')

    mfobj = pymeshfix.MeshFix()
    mfobj.LoadFile(filename)
    mfobj.PlotInput()
    mfobj.Repair()
    mfobj.DisplayFixedSurface()
