import os

import numpy as np
import pymeshfix
from pymeshfix.examples import bunny_scan

def test_native():
    out_file = 'repaired.ply'

    # test write permissions
    curdir = os.getcwd()
    if not os.access(curdir, os.W_OK):
        raise Exception('Cannot write output mesh here at %s' % curdir)

    pymeshfix._meshfix.CleanFromFile(bunny_scan, out_file, verbose=False)

    # this requires vtk and makes testing complicated...
    # outmesh = vtki.PolyData(out_file)
    # os.remove(out_file)
    # assert outmesh.GetNumberOfPoints()

    # # test for any holes
    # pdata = outmesh.ExtractEdges(non_manifold_edges=False, feature_edges=False,
    #                              manifold_edges=False)
    # assert pdata.GetNumberOfPoints() == 0
