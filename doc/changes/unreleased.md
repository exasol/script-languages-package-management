# Unreleased

## Features

 - #1: Created skeletal structure for this project
 - #3: Created CLI for install commands
 - #12: Integration Test FW
 - #27: Added executables to release
 - #29: Changed Github workflows to run tests on ARM
 - #26: Migrated to PEP 621 - a new format for pyproject.toml 
 - #31: Added new Add/Remove package API
 - #37: Added schema version to Pydantic Model
 - #35: Implemented build-steps history mechanism 
 - #40: Added the Install Binaries section (pip, microconda, bazel) and PPA section to the model.
 - #42: Added DockerCommandExecutor test framework
 - #35: Implemented build-steps history mechanism
 - #44: Implemented find methods for binaries and variables
 - #11: Implemented install_python_pip command
 - #54: Added find_pip method
 - #56: Added field "install_build_tools_ephemerally` to PipPackages
 - #58: Added field needs-break-system-packages to Pip
 - #5: Implemented install command for PIP packages
 - #64: Added environment variables to CommandExecutor
 - #62: Added ValidationCfg model and implemented usage of field URL of PipPackage
 - #8: Implemented install_micromamba command
 - #6: Implemented install_conda_packages command
 - #9: Implemented install_ppa
 - #4: Implement install command for R
 - #70: Added Bazel install
 - #75: Added Github Workflow which creates docker images
 - #85: Added order to build step history
 - #88: Added export variables function
 - #92: Added logic to treat variable values as Jinja2 templates

## Refactorings

 - #48: Updated model validation to restrict each phase to a single entry of (apt/r/conda/pip/tools)
 - #46: Refactored injection of classes which implement external dependencies
 - #49: Updated install_packages to process all phases of a build step
 - #36: Added unit tests for exasol.exaslpm.pkg_mgmt.install_packages.package_install
 - #73: Updated to PTB 5.1.1 and relocked dependencies
 - #59: Extend integration tests to run on different versions of Ubuntu
 - #79: Build executables for oldest supported Ubuntu version

## Bugs

 - #82: Cleaned up LD_LIBRARY_PATH for subprocesses