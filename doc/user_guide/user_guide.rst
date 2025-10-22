.. _user_guide:

User Guide
==========

About
-----
This project installs different packages and dependencies from the specified channel sources. It can be thought of one-stop-shop for all installation requirements. It uses an yaml file containing details of packages and their version to be installed.

Requirements
------------
Supported OS: Ubuntu >= 22.04

Getting Started
---------------

Download the standalone executable ``exaslpm``, for linux, from `release-page <https://github.com/exasol/integration-test-docker-environment/releases>`_. Once downloaded, it can be run as follows

::

   exaslpm --help

Installing packages
-------------------
This tool comes up with a list of command line options for installing packages specific installer and channel sources. Following are those options.
::

   Usage: exaslpm install [OPTIONS]

   Options:
    --phase TEXT
                                Name of the phase. This can be Phase 1, Phase 2 and so on.
    
    --package-file pkg_details.yaml
                                The yaml file containing the details of the package.

    --build-step
                                Name of the build dependencies

    --python-binary
    --conda-binary
    --r-binary 
                                These are used to point to channel sources to install from