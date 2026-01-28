"""
Cow Mesh Repair
---------------

Repair a mesh of a cow.
"""

import numpy as np

# sphinx_gallery_thumbnail_number = 1
import pyvista as pv
from pyvista import examples

import pymeshfix as mf

################################################################################
cow = examples.download_cow()

# Add holes and cast to triangulated PolyData
cow["random"] = np.random.rand(cow.n_cells)
holy_cow = cow.threshold(0.9, invert=True).extract_geometry().triangulate()
print(holy_cow)

################################################################################

# A nice camera location of the cow
cpos = [(6.56, 8.73, 22.03), (0.77, -0.44, 0.0), (-0.13, 0.93, -0.35)]

meshfix = mf.MeshFix(holy_cow)
holes = meshfix.extract_holes()

# Render the mesh and outline the holes
p = pv.Plotter()
p.add_mesh(holy_cow, color=True, smooth_shading=True, split_sharp_edges=True)
p.add_mesh(holes, color="r", line_width=8)
p.camera_position = cpos
p.camera.zoom(1.5)
p.enable_eye_dome_lighting()  # helps depth perception
p.enable_anti_aliasing("ssaa")
p.show()


################################################################################
# Repair the holey cow

meshfix.repair(verbose=True)

################################################################################
# Show the repaired result

repaired = meshfix.mesh
print(repaired)

################################################################################
repaired.plot(cpos=cpos, zoom=1.5, smooth_shading=True, split_sharp_edges=True)
