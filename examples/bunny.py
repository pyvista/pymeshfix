"""
Bunny
-----

Repair the holes in the bunny mesh.
"""

# sphinx_gallery_thumbnail_number = 2
import pyvista as pv
from pyvista import examples

import pymeshfix as mf

################################################################################
bunny = examples.download_bunny()

# Define a camera position that shows the holes in the mesh
cpos = [(-0.2, -0.13, 0.12), (-0.015, 0.10, -0.0), (0.28, 0.26, 0.9)]

# Show mesh
bunny.plot(cpos=cpos)

################################################################################
# Generate a meshfix mesh ready for fixing and extract the holes
meshfix = mf.MeshFix(bunny)
holes = meshfix.extract_holes()

################################################################################
# Render the mesh and outline the holes
p = pv.Plotter()
p.add_mesh(bunny, color=True)
p.add_mesh(holes, color="r", line_width=8)
p.camera_position = cpos
p.enable_eye_dome_lighting()  # helps depth perception
p.show()

################################################################################
# Repair the mesh
meshfix.repair(verbose=True)

################################################################################
# Show the repaired mesh
meshfix.mesh.plot(cpos=cpos)
