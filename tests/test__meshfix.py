from pathlib import Path
import numpy as np
from pymeshfix import _meshfix, examples
from pymeshfix.meshfix import _polydata_from_faces
import pytest
import pyvista as pv

bunny = pv.PolyData(examples.bunny_scan)
bunny.points = bunny.points.astype(np.float64)


def test_load_array() -> None:
    mfix = _meshfix.PyTMesh()
    assert mfix.n_faces == 0
    v = bunny.points
    with pytest.raises(TypeError):
        mfix.load_array(v, bunny.faces)

    f = bunny._connectivity_array.reshape(-1, 3).astype(np.int32, copy=False)
    mfix.load_array(v, f)
    with pytest.raises(RuntimeError, match="Cannot load arrays after arrays have"):
        mfix.load_array(v, f)

    # expect the number of points to be identical if connectivity is not changed
    assert mfix.n_faces == bunny.n_cells
    # assert mfix.n_points == bunny.n_points, connectivity has changed

    v_out, f_out = mfix.return_arrays()
    # assert np.array_equal(v, v_out)
    assert f.shape == f_out.shape


def test_load_and_save_file(tmp_path: Path) -> None:
    mfix = _meshfix.PyTMesh()
    mfix.set_quiet(1)
    mfix.load_file(examples.bunny_scan)

    with pytest.raises(RuntimeError):
        mfix.load_file(examples.bunny_scan)

    v, f = mfix.return_arrays()
    assert f.shape[0] == bunny.n_cells

    # test saving
    filename = str(tmp_path / "tmp.ply")
    mfix.save_file(filename)
    new_bunny = pv.PolyData(filename)
    assert new_bunny.n_points == v.shape[0]


def test_clean_from_file() -> None:
    mfix = _meshfix.PyTMesh()
    mfix.set_quiet(1)
    mfix.load_file(examples.bunny_scan)

    assert mfix.n_boundaries

    mfix.clean()
    assert not mfix.n_boundaries

    v, f = mfix.return_arrays()
    mesh = _polydata_from_faces(v, f)
    hole_edges = mesh.extract_feature_edges(
        boundary_edges=True, feature_edges=False, manifold_edges=False
    )
    assert not hole_edges.n_cells


def test_clean_from_arrays() -> None:
    v = bunny.points
    f = bunny._connectivity_array.reshape(-1, 3).astype(np.int32, copy=False)

    mfix = _meshfix.PyTMesh()
    mfix.load_array(v, f)
    assert mfix.n_boundaries

    mfix.clean()
    assert not mfix.n_boundaries

    v, f = mfix.return_arrays()
    mesh = _polydata_from_faces(v, f)
    hole_edges = mesh.extract_feature_edges(
        boundary_edges=True, feature_edges=False, manifold_edges=False
    )
    assert not hole_edges.n_cells


def test_fill_small_boundaries() -> None:
    mfix = _meshfix.PyTMesh()
    mfix.set_quiet(1)
    mfix.load_file(examples.bunny_scan)
    n_init_boundaries = mfix.n_boundaries

    n_filled = mfix.fill_small_boundaries(refine=False)
    assert n_filled
    assert mfix.n_boundaries < n_init_boundaries


def test_remove_components() -> None:
    mfix = _meshfix.PyTMesh()
    mfix.set_quiet(1)
    mfix.load_file(examples.bunny_scan)
    assert mfix.remove_smallest_components()


def test_select_intersecting_triangles() -> None:
    mfix = _meshfix.PyTMesh()
    mfix.load_file(examples.bunny_scan)
    faces = mfix.select_intersecting_triangles()
    assert faces.any()


def test_clean_from_file(tmp_path: Path) -> None:
    outfile = str(tmp_path / "tmp.ply")
    _meshfix.clean_from_file(examples.bunny_scan, outfile, verbose=False, joincomp=False)

    mfix = _meshfix.PyTMesh()
    mfix.load_file(outfile)
    assert not mfix.n_boundaries


def test_native_example(tmp_path) -> None:
    outfile = tmp_path / "tmp2.ply"
    examples.native(str(outfile))
    assert outfile.exists()
