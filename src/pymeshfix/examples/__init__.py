"""Built-in examples."""

# get location of the example meshes
from os.path import dirname, join, realpath

pth = dirname(realpath(__file__))
bunny_scan = join(pth, "StanfordBunny.ply")
planar_mesh = join(pth, "planar_mesh.ply")

from pymeshfix.examples.fix import native, with_vtk  # noqa: F401, E402
