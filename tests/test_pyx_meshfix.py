from pymeshfix import _meshfix, examples
import pytest
import pyvista as pv

bunny = pv.PolyData(examples.bunny_scan)


def test_load_and_save_file(tmpdir):
    meshfix = _meshfix.PyTMesh()
    meshfix.load_file(examples.bunny_scan)

    with pytest.raises(Exception):
        meshfix.load_file(examples.bunny_scan)

    v, f = meshfix.return_arrays()
    assert f.shape[0] == bunny.n_faces

    # test saving
    filename = str(tmpdir.mkdir("tmpdir").join("tmp.ply"))
    meshfix.save_file(filename)
    new_bunny = pv.PolyData(filename)
    assert new_bunny.points.shape == v.shape


def test_load_array():
    meshfix = _meshfix.PyTMesh()
    v = bunny.points
    with pytest.raises(Exception):
        meshfix.load_array(v, bunny.faces)

    f = bunny.faces.reshape(-1, 4)[:, 1:]
    meshfix.load_array(v, f)
    v, f = meshfix.return_arrays()
    assert f.shape[0] == bunny.n_faces

    with pytest.raises(Exception):
        meshfix.load_array(v, f)


def test_clean():
    meshfix = _meshfix.PyTMesh()
    meshfix.load_file(examples.bunny_scan)
    # v, f = meshfix.return_arrays()
    # assert f.shape[0] == bunny.n_faces

    assert meshfix.boundaries()

    meshfix.clean()
    assert not meshfix.boundaries()


def test_fill_small_boundaries():
    meshfix = _meshfix.PyTMesh()
    meshfix.load_file(examples.bunny_scan)
    ninit_boundaries = meshfix.boundaries()

    meshfix.fill_small_boundaries(refine=False)
    assert meshfix.boundaries() < ninit_boundaries


def test_remove_components():
    meshfix = _meshfix.PyTMesh()
    meshfix.load_file(examples.bunny_scan)
    assert meshfix.remove_smallest_components()


def test_select_intersecting_triangles():
    meshfix = _meshfix.PyTMesh(verbose=0)
    meshfix.load_file(examples.bunny_scan)
    faces = meshfix.select_intersecting_triangles()
    assert faces.any()


def clean_from_file(tmpdir):
    outfile = str(tmpdir.mkdir("tmpdir").join("tmp.ply"))
    clean_from_file(examples.bunny_scan, outfile, verbose=False, joincomp=False)
    outfile = str(tmpdir.mkdir("tmpdir").join("tmp2.ply"))
    examples.native(outfile)
