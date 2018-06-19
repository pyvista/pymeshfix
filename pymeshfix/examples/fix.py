""" Demonstrates mesh repair on the standford bunny mesh """

from os.path import dirname, join, realpath
import pymeshfix
import vtkInterface as vtki

# get location of the example mesh
pth = dirname(realpath(__file__))
filename = join(pth, 'StanfordBunny.ply')


def Native():
    """ Repair Stanford Bunny Mesh """
    # get location of this file
    pymeshfix._meshfix.CleanFromFile(filename, 'repaired.ply')


def WithVTK(plot=True):
    """ Tests VTK interface and mesh repair of Stanford Bunny Mesh """
    mesh = vtki.PolyData(filename)
    meshfix = pymeshfix.MeshFix(mesh)
    if plot:
        print('Plotting input mesh')
        meshfix.Plot()
    meshfix.Repair()
    if plot:
        print('Plotting repaired mesh')
        meshfix.Plot()

    return meshfix.mesh


# ideally would use pytest.  We're getting there...
if __name__ == '__main__':
    """ doubles as a test """
    Native()

    # mesh = WithVTK(False)
    # pdata = mesh.ExtractEdges(non_manifold_edges=False, feature_edges=False,
    #                           manifold_edges=False)
    # try:
    #     assert mesh.GetNumberOfPoints()
    #     assert pdata.GetNumberOfPoints() == 0
    #     print('TESTS PASSED')
    # except Exception as e:
    #     raise Exception('TESTS FAILED %s' % str(e))


