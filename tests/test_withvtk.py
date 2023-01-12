import numpy as np
import pymeshfix
from pymeshfix.examples import bunny_scan
import pyvista as pv


def test_repair_vtk():
    meshin = pv.PolyData(bunny_scan)
    meshfix = pymeshfix.MeshFix(meshin)
    meshfix.repair()

    # check arrays and output mesh
    assert np.any(meshfix.v)
    assert np.any(meshfix.f)
    meshout = meshfix.mesh
    assert meshfix.mesh.n_points

    # test for any holes
    pdata = meshout.extract_feature_edges(
        non_manifold_edges=False, feature_edges=False, manifold_edges=False
    )
    assert pdata.n_points == 0
