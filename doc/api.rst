.. _api:

:octicon:`cpu` API Reference
=============================

Package Editor
--------------

The package editor module allows manipulation of an existing package file:
    - Update comments
    - Update names
    - Add new packages to APT/Conda/Pip/R package lists
    - Remove packages from APT/Conda/Pip/R package lists

Create an instance of class ``exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_file_editor.PackageFileEditor`` to edit an existing package file.

.. autosummary::
   :toctree: api
   :recursive:

    exasol.exaslpm.pkg_mgmt.pkg_file_editor

.. autoclass:: exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_file_editor.PackageFileEditor
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:

.. autoclass:: exasol.exaslpm.pkg_mgmt.pkg_file_editor.build_step_editor.BuildStepEditor
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:


.. autoclass:: exasol.exaslpm.pkg_mgmt.pkg_file_editor.phase_editor.PhaseEditor
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:

.. autoclass:: exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_editors.AptPackageEditor
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:

.. autoclass:: exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_editors.CondaPackageEditor
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:


.. autoclass:: exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_editors.RPackageEditor
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:

.. autoclass:: exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_editors.PipPackageEditor
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:
