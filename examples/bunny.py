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
bunny.plot(cpos=cpos, eye_dome_lighting=True, anti_aliasing=True, smooth_shading=True)

################################################################################
# Generate a meshfix mesh ready for fixing and extract the holes
mfix = mf.MeshFix(bunny)
holes = mfix.extract_holes()

################################################################################
# Render the mesh and outline the holes
pl = pv.Plotter()
pl.add_mesh(bunny, color=True, smooth_shading=True)
pl.add_mesh(holes, color="r", line_width=12, render_lines_as_tubes=True, lighting=False)
pl.camera_position = cpos
pl.enable_eye_dome_lighting()  # helps depth perception
pl.enable_anti_aliasing("ssaa")
pl.show()

################################################################################
# Repair the mesh
mfix.repair(verbose=True)

################################################################################
# Show the repaired mesh
mfix.mesh.plot(cpos=cpos, eye_dome_lighting=True, anti_aliasing=True, smooth_shading=True)
