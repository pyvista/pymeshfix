"""
Holey Cow
---------

Repair a holey cow
"""

# sphinx_gallery_thumbnail_number = 1
import pyvista as pv
import pymeshfix as mf
from pyvista import examples
import numpy as np

################################################################################
cow = examples.download_cow()

# Add holes and cast to triangulated PolyData
cow['random'] = np.random.rand(cow.n_cells)
holy_cow = cow.threshold(0.9, invert=True).extract_geometry().triangulate()
print(holy_cow)

################################################################################

# A nice camera location of the cow
cpos= [(6.56, 8.73, 22.03),
       (0.77, -0.44, 0.0),
       (-0.13, 0.93, -0.35)]

meshfix = mf.MeshFix(holy_cow)
holes = meshfix.extract_holes()

# Render the mesh and outline the holes
p = pv.Plotter()
p.add_mesh(holy_cow, color=True)
p.add_mesh(holes, color='r', line_width=8)
p.camera_position = cpos
p.enable_eye_dome_lighting() # helps depth perception
p.show()


################################################################################
# Repair the holey cow

meshfix.repair(verbose=True)

################################################################################
# Show the repaired result

repaired = meshfix.mesh
print(repaired)

################################################################################
repaired.plot(cpos=cpos)
