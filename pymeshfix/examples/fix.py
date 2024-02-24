"""Demonstrate mesh repair on the standford bunny mesh."""

import os
import time

import numpy as np
import pyvista as pv

import pymeshfix
from pymeshfix.examples import bunny_scan


def native(outfile="repaired.ply"):
    """Repair the Stanford Bunny Mesh using the low level API."""
    pymeshfix._meshfix.clean_from_file(bunny_scan, outfile)
    return outfile


def with_vtk(plot=True):
    """Tests VTK interface and mesh repair of Stanford Bunny Mesh"""
    mesh = pv.PolyData(bunny_scan)
    meshfix = pymeshfix.MeshFix(mesh)
    if plot:
        print("Plotting input mesh")
        meshfix.plot()
    meshfix.repair()
    if plot:
        print("Plotting repaired mesh")
        meshfix.plot()

    return meshfix.mesh


if __name__ == "__main__":
    """Functional Test: vtk and native"""
    t_start = time.time()
    out_file = "repaired.ply"
    native()
    outmesh = pv.PolyData(out_file)
    os.remove(out_file)
    assert outmesh.n_points

    # test for any holes
    pdata = outmesh.extract_edges(
        non_manifold_edges=False, feature_edges=False, manifold_edges=False
    )
    assert pdata.n_points == 0

    # test vtk
    meshin = pv.PolyData(bunny_scan)
    meshfix = pymeshfix.MeshFix(meshin)
    meshfix.repair()

    # check arrays and output mesh
    assert np.any(meshfix.v)
    assert np.any(meshfix.f)
    meshout = meshfix.mesh
    assert meshfix.mesh.n_points

    # test for any holes
    pdata = meshout.extract_edges(
        non_manifold_edges=False, feature_edges=False, manifold_edges=False
    )
    print("PASS in %f seconds" % (time.time() - t_start))
