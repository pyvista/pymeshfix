"""
Cow
---

Repair the cow that became split in half
"""

# sphinx_gallery_thumbnail_number = 2
import pyvista as pv
import pymeshfix as mf
from pyvista import examples

################################################################################
cow = examples.download_cow()

# Split the cow
split_cow = cow.clip_box()
