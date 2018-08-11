import os

import numpy as np
import pymeshfix
from pymeshfix.examples import bunny_scan

import vtkInterface as vtki

def test_repairVTK():
    meshin = vtki.PolyData(bunny_scan)
    meshfix = pymeshfix.MeshFix(meshin)
    meshfix.Repair()

    # check arrays and output mesh
    assert np.any(meshfix.v)
    assert np.any(meshfix.f)
    meshout = meshfix.mesh
    assert meshfix.mesh.GetNumberOfPoints()

    # test for any holes
    pdata = meshout.ExtractEdges(non_manifold_edges=False, feature_edges=False,
                                 manifold_edges=False)
    assert pdata.GetNumberOfPoints() == 0
