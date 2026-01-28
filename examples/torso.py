"""
Torso
-----

Repair the torso mesh where it was extracted and subtle holes along complex
parts of the mesh
"""

# sphinx_gallery_thumbnail_number = 2
import pyvista as pv
from pyvista import examples

import pymeshfix as mf

mesh = examples.download_torso()
print(mesh)

################################################################################

cpos = [(-1053.0, -1251.0, 83.0), (2.0, -15.0, -276.0), (0.12, 0.18, 1)]

mesh.plot(color=True, show_edges=True, cpos=cpos)

################################################################################
# Apply a triangle filter to ensure the mesh contains only triangles.

meshfix = mf.MeshFix(mesh.triangulate(), verbose=True)
holes = meshfix.extract_holes()

################################################################################
# Outline the holes in the mesh
p = pv.Plotter()
p.add_mesh(mesh)
p.add_mesh(holes, color="r", line_width=8)
p.enable_eye_dome_lighting()  # helps with depth perception
p.camera_position = cpos
p.show()

################################################################################
# Emphasize the hole near the ear - this needs to be repaired so that the mesh
# is absolutely water tight.
cpos_ear = [(180.0, -206.0, 17.0), (107.0, -122.9, -11.9), (-0.13, 0.22, 0.96)]

p = pv.Plotter()
p.add_mesh(mesh)
p.add_mesh(holes, color="r", line_width=8)
p.enable_eye_dome_lighting()  # helps with depth perception
p.camera_position = cpos_ear
p.show()

################################################################################
# Perform the mesh repair
meshfix.repair()

################################################################################
# Show the repaired mesh
meshfix.mesh.plot(cpos=cpos, show_edges=True)
