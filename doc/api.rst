API Reference
=============
These are the two public classes that expose the meshfix API to
Python.  The pure Python python class is ``MeshFix``, which requires
``pyvista``.  The lower level cython extension of meshfix is
``PyTMesh``, which does not require `pyvista <https://docs.pyvista.org/>`__.


.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst

   pymeshfix.MeshFix
   pymeshfix.PyTMesh


Lower level convenience methods that expose the lower level
functionality of meshfix without using `pyvista <https://docs.pyvista.org/>`__.

.. autosummary::
   :toctree: _autosummary

   pymeshfix.clean_from_file
   pymeshfix.clean_from_arrays
