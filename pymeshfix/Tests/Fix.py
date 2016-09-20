""" Demonstrates mesh repair on the standford bunny mesh """
from os.path import dirname, join, realpath

#import numpy as np
from pymeshfix import _meshfix, meshfix

# get location of the example mesh
pth = dirname(realpath(__file__))
filename = join(pth, 'StanfordBunny.ply')


def Native():
    """ Repair Stanford Bunny Mesh """
    # get location of this file
    _meshfix.CleanFromFile(filename, 'repaired.ply')


def WithVTK():
    """ Tests VTK interface and mesh repair of Stanford Bunny Mesh """

    try:
        import vtk
    except:
        raise Exception('Install VTK to use this feature')
    
    mfobj = meshfix.MeshFixClass()
    mfobj.LoadFile(filename)
    mfobj.DisplayInputSurface()
    mfobj.Repair()
    mfobj.DisplayFixedSurface()

    
