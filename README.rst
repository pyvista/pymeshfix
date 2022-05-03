PyMeshFix
=========

.. |azure| image:: https://dev.azure.com/pyvista/PyVista/_apis/build/status/pyvista.pymeshfix?branchName=master
   :target: https://dev.azure.com/pyvista/PyVista/_build?definitionId=5

.. |pypi| image:: https://img.shields.io/pypi/v/pymeshfix.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pymeshfix/

Python/Cython wrapper of Marco Attene's wonderful, award-winning
`MeshFix <https://github.com/MarcoAttene/MeshFix-V2.1>`__ software.
This module brings the speed of C++ with the portability and ease of
installation of Python.

This software takes as input a polygon mesh and produces a copy of the input
where all the occurrences of a specific set of "defects" are corrected.
MeshFix has been designed to correct typical flaws present in raw digitized
mesh models, thus it might fail or produce coarse results
if run on other sorts of input meshes (e.g. tessellated CAD models).

The input is assumed to represent a single closed solid object, thus the output
will be a single watertight triangle mesh bounding a polyhedron.
All the singularities, self-intersections and degenerate elements are removed
from the input, while regions of the surface without defects are left
unmodified.

C++ source last updated 1 Jul 2020

Installation
------------

From `PyPI <https://pypi.python.org/pypi/pymeshfix>`__

.. code:: bash

    pip install pymeshfix

From source at `GitHub <https://github.com/pyvista/pymeshfix>`__

.. code:: bash

    git clone https://github.com/pyvista/pymeshfix
    cd pymeshfix
    pip install .


Dependencies
------------
Requires ``numpy`` and ``pyvista``

If you can't or don't want to install vtk, you can install it without
``pyvista`` with:

.. code:: bash

    pip install pymeshfix --no-dependencies

You'll miss out on some of the cool features from ``pyvista``, but it will still function.


Examples
--------
Test installation with the following from Python:

.. code:: python

    from pymeshfix import examples

    # Test of pymeshfix without VTK module
    examples.native()

    # Performs same mesh repair while leveraging VTK's plotting/mesh loading
    examples.with_vtk()


Easy Example
------------
This example uses the Cython wrapper directly. No bells or whistles here:

.. code:: python

    import pymeshfix

    # Read mesh from infile and output cleaned mesh to outfile
    pymeshfix.clean_from_file(infile, outfile)


This example assumes the user has vertex and faces arrays in Python.

.. code:: python

    import pymeshfix

    # Generate vertex and face arrays of cleaned mesh
    # where v and f are numpy arrays
    vclean, fclean = pymeshfix.clean_from_arrays(v, f)


Complete Examples with and without VTK
--------------------------------------
One of the main reasons to bring MeshFix to Python is to allow the
library to communicate to other python programs without having to use
the hard drive.  Therefore, this example assumes that you have a mesh
within memory and wish to repair it using MeshFix.

.. code:: python

    import pymeshfix

    # Create object from vertex and face arrays
    meshfix = pymeshfix.MeshFix(v, f)

    # Plot input
    meshfix.plot()

    # Repair input mesh
    meshfix.repair()

    # Access the repaired mesh with vtk
    mesh = meshfix.mesh

    # Or, access the resulting arrays directly from the object
    meshfix.v # numpy np.float64 array
    meshfix.f # numpy np.int32 array

    # View the repaired mesh (requires vtkInterface)
    meshfix.plot()

    # Save the mesh
    meshfix.write('out.ply')

Alternatively, the user could use the Cython wrapper of MeshFix directly if
vtk is unavailable or they wish to have more control over the cleaning
algorithm.

.. code:: python

    import pymeshfix

    # Create TMesh object
    tin = pymeshfix.PyTMesh()

    tin.LoadFile(infile)
    # tin.load_array(v, f) # or read arrays from memory

    # Attempt to join nearby components
    # tin.join_closest_components()

    # Fill holes
    tin.fill_small_boundaries()
    print('There are {:d} boundaries'.format(tin.boundaries()))

    # Clean (removes self intersections)
    tin.clean(max_iters=10, inner_loops=3)

    # Check mesh for holes again
    print('There are {:d} boundaries'.format(tin.boundaries()))

    # Clean again if necessary...

    # Output mesh
    tin.save_file(outfile)

     # or return numpy arrays
    vclean, fclean = tin.return_arrays()


Algorithm and Citation Policy
-----------------------------

To better understand how the algorithm works, please refer to the following
paper:

    M. Attene. A lightweight approach to repairing digitized polygon meshes.
    The Visual Computer, 2010. (c) Springer. DOI: 10.1007/s00371-010-0416-3

This software is based on ideas published therein. If you use MeshFix for
research purposes you should cite the above paper in your published results.
MeshFix cannot be used for commercial purposes without a proper licensing
contract.


Copyright
---------

MeshFix is Copyright(C) 2010: IMATI-GE / CNR

All rights reserved.

This program is dual-licensed as follows:

(1) You may use MeshFix as free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

In this case the program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
(http://www.gnu.org/licenses/gpl.txt) for more details.

(2) You may use MeshFix as part of a commercial software. In this case a proper
agreement must be reached with the Authors and with IMATI-GE/CNR based on a
proper licensing contract.
