pymeshfix
=========

Python/Cython wrapper of Marco Attene's wonderful, award-winning
`MeshFix <https://github.com/MarcoAttene/MeshFix-V2.0>`__ software. This
module brings the speed of C++ with the portability and ease of
installation of Python.

This software takes as input a polygon mesh and produces a copy of the
input where all the occurrences of a specific set of "defects" are
corrected. MeshFix has been designed to correct typical flaws present in
RAW DIGITIZED mesh models, thus it might fail or produce coarse results
if run on other sorts of input meshes (e.g. tessellated CAD models).

The input is assumed to represent a single CLOSED SOLID OBJECT, thus the
output will be a SINGLE WATERTIGHT TRIANGLE MESH bounding a polyhedron.
All the singularities, self-intersections and degenerate elements are
removed from the input, while regions of the surface without defects are
left unmodified.

Installation
------------

From `PyPI <https://pypi.python.org/pypi/pymeshfix>`__

.. code:: bash

    pip install pymeshfix

From source at `GitHub (https://github.com/akaszynski/pymeshfix`__

.. code:: bash

    git clone --recursive https://github.com/akaszynski/pymeshfix
    cd pymeshfix
    pip install .

Dependencies
------------

Required: ``numpy``, ``cython``. Optional: ``vtk``

Minimum requirements are numpy and cython. To enable plotting and
several other features, vtk 5.0 or greater must be installed with Python
bindings. VTK can be installed through a variety of methods. Please see
http://www.vtk.org/

Tests
-----

Test installation with the following from Python

.. code:: python

    from pymeshfix import Tests

    # Test of pymeshfix without VTK module
    Tests.Fix.Native()

    # Performs same mesh repair while leveraging VTK's plotting/mesh loading
    Tests.Fix.WithVTK()

Easy Example
------------

This example uses the cython wrapper directly. No bells or whistles
here.

.. code:: python

    from pymeshfix import _meshfix

    # Read mesh from infile and output cleaned mesh to outfile
    _meshfix.CleanFromFile(infile, outfile)

This example assumes the user has vertex and faces arrays in Python.
Again, no bells or whistles.

.. code:: python

    from pymeshfix import _meshfix

    # Generate vertex and face arrays of cleaned mesh
    vclean, fclean = CleanFromVF(v, f) # v and f are numpy arrays or python lists

Fuller Examples with and without VTK
------------------------------------

One of the main reasons to bring MeshFix to Python is to allow the
library to communicate to other python programs without having to use
the hard drive. Therefore, this example assumes that you have a mesh
within memory and wish to repair it using MeshFix.

.. code:: python

    #Load module
    from pymeshfix import meshfix

    # Create object
    mfobj = meshfix.MeshFixClass()
    mfobj.LoadVF(v, f) # from arrays or lists
    #mfobj.LoadFile(filename) # or from file
    #mfobj.LoadMesh(vtkpoly) # or from a vtk.vtkPolyData object

    # Plot input (if vtk is available)
    mfobj.DisplayInputSurface()

    # Repair input mesh
    mfobj.Repair()

    # Generate vtk output mesh\
    mfobj.GenFixedMesh() # creates mfobj.grid

    # Or, access the resulting arrays directly from the object
    mfobj.vclean # numpy np.float array
    mfobj.fclean # numpy np.int32 array

    # View the repaired mesh
    mfobj.DisplayFixedSurface()

    # Save the mesh
    mfobj.SaveFixedMesh('out.ply')

Alternatively, the user could use the cython wrapper of MeshFix directly
if vtk is unavailable or they wish to have more control over the
cleaning algorthim.

.. code:: python

    from pymeshfix import _meshfix

    # Create TMesh object
    tin = _meshfix.PyTMesh()

    tin.LoadFile(infile)
    # tin.LoadArray(v, f) # can also read arrays from memory

    # Attempt to join nearby components
    # tin.JoinClosestComponents()

    # Fill holes
    tin.FillSmallBoundaries()
    print('There are {:d} boundaries'.format(tin.Boundaries())

    # Clean (removes self intersections)
    tin.MeshClean(max_iters=10, inner_loops=3)

    # Check mesh for holes again
    print('There are {:d} boundaries'.format(tin.Boundaries())

    # Clean again if necessary...

    # Output mesh
    tin.SaveFile(outfile)
    # vclean, fclean = tin.ReturnArrays() # returns numpy arrays

Algorithim and Citation Policy
------------------------------

To better understand how the algorithm works, please refer to the
following paper:

M. Attene. A lightweight approach to repairing digitized polygon meshes.
The Visual Computer, 2010. (c) Springer. DOI: 10.1007/s00371-010-0416-3

This software is based on ideas published therein. If you use MeshFix
for research purposes you should cite the above paper in your published
results. MeshFix cannot be used for commercial purposes without a proper
licensing contract.

Copyright
---------

MeshFix is

Copyright(C) 2010: IMATI-GE / CNR

All rights reserved.

This program is dual-licensed as follows:

(1) You may use MeshFix as free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 3 of the
    License, or (at your option) any later version.

In this case the program is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License (http://www.gnu.org/licenses/gpl.txt) for more details.

(2) You may use MeshFix as part of a commercial software. In this case a
    proper agreement must be reached with the Authors and with
    IMATI-GE/CNR based on a proper licensing contract.

