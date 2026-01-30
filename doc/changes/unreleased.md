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

## Refactorings

 - #48: Updated model validation to restrict each phase to a single entry of (apt/r/conda/pip/tools)
 - #46: Refactored injection of classes which implement external dependencies
 - #49: Updated install_packages to process all phases of a build step
 - #36: Added unit tests for exasol.exaslpm.pkg_mgmt.install_packages.package_install