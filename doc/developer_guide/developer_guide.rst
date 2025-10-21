.. _developer_guide:

===============
Developer Guide
===============

``exaslpm`` is a tool for installing packages from different source channels using different installers like apt, pip, conda, etc... This document explains internals of this tool.

Preparation
===========
Get the environment up and running.

Requirements
~~~~~~~~~~~~
Supported OS: Ubuntu >= 22.04

Install Poetry
~~~~~~~~~~~~~~

``sudo apt install python3-poetry``

Install dependencies
~~~~~~~~~~~~~~~~~~~~
``poetry install``

Creating a Standalone Executable
================================
A standalone executable for linux environment can be created as follows. It will be created under ``dist`` folder.

.. code-block:: shell

   poetry run -- nox -s build-standalone-binary -- --executable-name "exaslpm"


Creating a Release
==================

Prerequisites
~~~~~~~~~~~~~

* Change log needs to be up to date
* ``unreleased`` change log version needs to be up-to-date
* Release tag needs to match package

  For Example:
        * Tag: 0.4.0
        * \`poetry version -s\`: 0.4.0

Preparing the Release
~~~~~~~~~~~~~~~~~~~~~
Run the following nox task in order to prepare the changelog.

    .. code-block:: shell

        poetry run -- nox -s release:prepare

Triggering the Release
~~~~~~~~~~~~~~~~~~~~~~
In order to trigger a release a new tag must be pushed to Github.

    .. code-block:: shell

        poetry run -- nox -s release:trigger

What to do if the release failed?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The release failed during pre-release checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Delete the local tag

    .. code-block:: shell

        git tag -d x.y.z

#. Delete the remote tag

    .. code-block:: shell

        git push --delete origin x.y.z

#. Fix the issue(s) which lead to the failing checks
#. Start the release process from the beginning


One of the release steps failed (Partial Release)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#. Check the Github action/workflow to see which steps failed
#. Finish or redo the failed release steps manually

.. note:: Example

    **Scenario**: Publishing of the release on Github was successfully but during the PyPi release, the upload step got interrupted.

    **Solution**: Manually push the package to PyPi

Running Tests
=============

You can execute all tests in a single file with the following command:

.. code-block:: shell

  poetry run -- nox -s test:unit -- --coverage
  poetry run -- nox -s test:integration

