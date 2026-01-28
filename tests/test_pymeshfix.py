from pathlib import Path
import numpy as np
import pytest
import pymeshfix
from pymeshfix.examples import bunny_scan
from pymeshfix.meshfix import InvalidMeshFixInputError
import pyvista as pv


def test_version() -> None:
    assert pymeshfix.__version__ != "unknown"


def test_repair_vtk() -> None:
    meshin = pv.PolyData(bunny_scan)
    mfix = pymeshfix.MeshFix(meshin)
    mfix.repair()

    # check arrays and output mesh
    assert np.any(mfix.points)
    assert np.any(mfix.faces)
    meshout = mfix.mesh
    assert mfix.mesh.n_points

    # test for any holes
    pdata = meshout.extract_feature_edges(
        non_manifold_edges=False, feature_edges=False, manifold_edges=False
    )
    assert pdata.n_points == 0


def test_repair_incremental() -> None:
    meshin = pv.PolyData(bunny_scan)
    mfix = pymeshfix.MeshFix(meshin, verbose=False)
    assert mfix.n_boundaries
    assert mfix.degeneracy_removal()
    assert mfix.intersection_removal()
    assert not mfix.fill_holes()  # should be no holes after degeneracy removal
    assert not mfix.n_boundaries


def test_from_filename() -> None:
    mfix = pymeshfix.MeshFix(bunny_scan)
    assert mfix.points.shape[0]
    assert mfix.faces.shape[0]

    mfix = pymeshfix.MeshFix(Path(bunny_scan))
    assert mfix.points.shape[0]
    assert mfix.faces.shape[0]


def test_from_arrays() -> None:
    with pytest.raises(InvalidMeshFixInputError):
        pymeshfix.MeshFix()

    meshin = pv.PolyData(bunny_scan)
    f = meshin._connectivity_array.reshape(-1, 3).astype(np.int32, copy=False)

    mfix = pymeshfix.MeshFix(meshin.points, f)
    assert mfix.points.shape[0]
    assert mfix.faces.shape[0]
