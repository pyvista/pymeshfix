"""
Torso
-----

Repair the torso mesh where it was extracted and subtle holes along complex
parts of the mesh
"""

# sphinx_gallery_thumbnail_number = 2
import pyvista as pv
import pymeshfix as mf
from pyvista import examples


mesh = examples.download_torso()
print(mesh)

################################################################################

cpos = [(-1053., -1251., 83.),
        (2., -15., -276.),
        (0.12, 0.18, 1)]

mesh.plot(color=True, show_edges=True, cpos=cpos)

################################################################################
# Appy a triangle filter to ensure the mesh is simply polyhedral
meshfix = mf.MeshFix(mesh.tri_filter())
holes = meshfix.extract_holes()

################################################################################
# Outline the holes in the mesh
p = pv.Plotter()
p.add_mesh(mesh)
p.add_mesh(holes, color='r', line_width=8)
p.enable_eye_dome_lighting() # helps with depth perception
p.camera_position = cpos
p.show()

################################################################################
# Emphasize the hole near the ear - this needs to be repaired so that the mesh
# is absolutely water tight.
cpos_ear = [(180., -206., 17.),
            (107., -122.9, -11.9),
            (-0.13, 0.22, 0.96)]

p = pv.Plotter()
p.add_mesh(mesh)
p.add_mesh(holes, color='r', line_width=8)
p.enable_eye_dome_lighting() # helps with depth perception
p.camera_position = cpos_ear
p.show()

################################################################################
# Perfrom the mesh repair
meshfix.repair(verbose=True)

################################################################################
# Show the repaired mesh
meshfix.mesh.plot(cpos=cpos, eye_dome_lighting=True)
