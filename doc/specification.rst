.. _specification:

Project Specification (Given-When-Then)
=======================================

Overview
--------
This specification documents behavior directly from the current implementation,
covering CLI invocation, package-file parsing and validation, phase execution,
installer-specific behavior, search resolution across history, and history
persistence.

CLI and Command Orchestration
-----------------------------

Scenario: Install command requires package file and build step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given the ``exaslpm`` CLI
When a user calls ``install``
Then the command requires ``--package-file`` as an existing path
And the command requires ``--build-step`` as a string.

Scenario: Install command initializes runtime context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given the install command is invoked with valid options
When command execution starts
Then it creates a standard logger and command executor
And it creates context services for history, file access, downloads, and temp files
And it calls the package installation orchestration function with those objects.

Scenario: Installation starts with build-step history guard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a requested build-step name
When ``package_install`` starts
Then the build-step name is checked against history before package-file loading
And execution stops if that build step was already processed.

Scenario: Package file loading failure is reported and re-raised
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given an unreadable, malformed, or invalid package file
When ``PackageFileSession`` creation fails
Then an error log entry is emitted with message ``Failed to read package file.``
And the original exception is re-raised.

Scenario: Missing build step is reported and re-raised
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a valid package file without the requested build-step name
When build-step lookup runs
Then an error log entry is emitted with message ``Build step not found.``
And the original exception is re-raised.

Scenario: Phases are processed sequentially
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a resolved build step containing phases
When orchestration executes
Then phases are processed in declared order
And each phase emits an info log ``Processing phase:'<phase-name>'``.

Scenario: Phase processing errors are wrapped with phase context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a phase that raises during processing
When orchestration catches the error
Then an error log includes both phase and build-step names
And the exception is re-raised.

Scenario: Successful installation persists build-step history
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given all phases complete without errors
When orchestration finishes
Then the build step is serialized and written to the history directory.

Phase Processing Rules
----------------------

Scenario: Apt repositories are installed before apt packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a phase containing both ``apt.repos`` and ``apt.packages``
When phase processing runs
Then repository installation executes first
And package installation executes second.

Scenario: Apt installer warns for empty package list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a phase with an apt installer section and zero packages
When apt package installation runs
Then no apt install command is executed
And a warning ``Got an empty list of AptPackages`` is logged.

Scenario: Apt installer command sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a phase with one or more apt packages
When apt package installation runs
Then commands are executed in this order:
And ``apt-get -y update``
And ``apt-get install -V -y --no-install-recommends <packages>``
And ``apt-get -y clean``
And ``apt-get -y autoremove``
And ``locale-gen en_US.UTF-8``
And ``update-locale LC_ALL=en_US.UTF-8``
And ``ldconfig``.

Scenario: Apt repository installation details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a configured apt repository
When apt repository installation runs
Then the repository key is downloaded and converted via ``gpg --dearmor``
And the key is written under ``/usr/share/keyrings/<repo>.gpg``
And the repository entry is written to ``/etc/apt/sources.list.d/<out_file>``
And apt update, clean, and autoremove are executed after repository setup.

Scenario: Tools phase dispatches tool installers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a phase with a ``tools`` section
When phase processing runs
Then tool installers are called only for configured tool entries
And ``tools.pip`` triggers pip bootstrap installation
And ``tools.micromamba`` triggers micromamba binary installation and base env creation
And ``tools.bazel`` triggers bazel binary installation.

Scenario: Pip package installation resolves cumulative package set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a pip package phase
When pip package installation runs
Then packages are collected from all previous phases in scope plus current phase
And packages are written to a temporary requirements-style file
And installation runs through ``<python> -m pip install -r <temp-file>``.

Scenario: Pip package spec rendering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given pip packages with and without URL sources
When the temporary pip spec file is generated
Then URL packages are rendered as ``<name> @ <url>``
And regular packages are rendered as ``<name> <version>``.

Scenario: Pip build tools may be installed ephemerally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given ``install_build_tools_ephemerally`` is true on a pip phase
When pip package installation runs
Then build tools are installed via apt before pip installation
And build tools are purged and autoremoved after pip installation.

Scenario: Pip break-system-packages flag propagation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given the resolved pip tool config has ``needs_break_system_packages`` enabled
When pip bootstrap or pip package installation commands are assembled
Then ``--break-system-packages`` is appended to the pip command.

Scenario: Conda package installation resolves cumulative packages and channels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a conda phase with packages
When conda installation runs
Then package specs are collected from prior+current conda phases
And channels are collected as a set from prior+current conda phases
And specs are written to a temporary file
And conda installation runs with ``install --yes --file <spec-file>`` and channel args.

Scenario: Conda post-install cleanup and linker refresh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given conda package installation was invoked
When conda commands are prepared
Then a conda ``clean --all --yes --index-cache --tarballs`` command is executed
And ``ldconfig`` is executed afterward.

Scenario: Conda binary selection is driven by phase configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a conda phase declares a binary kind (Micromamba, Mamba, Conda)
When conda command execution is prepared
Then the selected binary path is resolved from search history rules
And command environment includes ``MAMBA_ROOT_PREFIX`` from micromamba settings.

Scenario: R package installation performs install and validation scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a phase with R packages
When R package installation runs
Then ``remotes`` is installed first from CRAN
And an R script is generated to install packages with ``install_version``
And a second R script is generated to validate installed package presence and versions.

Scenario: R installer warns for empty package list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given an R phase without packages
When R installation runs
Then no install script is executed
And a warning ``Got an empty list of R packages`` is logged.

Scenario: Micromamba installation by architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a tools phase with micromamba settings
When micromamba installation runs
Then the release URL is built from configured version and detected machine architecture
And only ``bin/micromamba`` is extracted to ``/`` from the downloaded archive
And a base environment is created using micromamba.

Scenario: Bazel installation by architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a tools phase with bazel settings
When bazel installation runs
Then the release URL is built from configured version and architecture mapping
And the downloaded binary is marked executable
And copied to ``/usr/bin/bazel``.

Search and Resolution Semantics
-------------------------------

Scenario: Search scope includes previous build steps and prior phases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a current build step and phase name
When a ``SearchCache`` is created
Then all phases from history build steps are included in search scope
And only phases before the current phase (not including current phase) are included from the current build step.

Scenario: Current phase must exist for scope creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a current phase name not present in the current build step
When phase-scope creation runs
Then a ``ValueError`` is raised indicating phase not found.

Scenario: Binary resolution uniqueness and existence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a requested binary type other than micromamba
When binary lookup runs across scoped phases
Then exactly one matching tools path must exist
And an error is raised if zero or multiple matches are found.

Scenario: Micromamba binary lookup is constant path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given micromamba binary resolution
When lookup runs
Then the path resolves directly to ``/bin/micromamba``.

Scenario: Resolved binaries are validated and cached
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a binary path is resolved for the first time
When accessed through ``SearchCache``
Then file-access binary checks are performed
And the resolved path is cached for subsequent access.

Scenario: Variable, pip, and micromamba lookups require uniqueness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given lookup for a variable, pip tool config, or micromamba tool config
When search runs across scope phases
Then exactly one matching entry must be found
And an error is raised if zero or multiple matches are found
And successful results are cached in ``SearchCache``.

Package-File Model and Validation
---------------------------------

Scenario: Package file version defaults to current schema version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given package-file input without explicit ``version``
When model validation runs
Then the version defaults to ``1.0.0``.

Scenario: Root validation always validates the model graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given deserialized package-file input
When the root model is validated
Then package-file graph validation is executed automatically.

Scenario: Minimum structure constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given package-file input
When graph validation runs
Then at least one build step is required
And every build step must have at least one phase.

Scenario: Name uniqueness constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given package-file input with duplicate names
When graph validation runs
Then duplicate build-step names are rejected
And duplicate phase names within a build step are rejected
And duplicate package names within installer package lists are rejected.

Scenario: Phase installer cardinality constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a phase definition
When graph validation runs
Then the phase must define at least one installer entry (including variables-only allowance)
And the phase must not define more than one installer among ``apt``, ``pip``, ``conda``, ``r``, and ``tools``.

Scenario: Package version requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given package entries for apt, conda, pip, and r installers
When graph validation runs with ``version_mandatory=true``
Then package versions are required for all installers
But pip packages with ``url`` are exempt from explicit version requirement.

Scenario: Apt repository key URLs require HTTP URL validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given apt repository definitions
When model validation runs
Then ``key_url`` must be a valid HTTP(S) URL.

Scenario: Find helpers enforce explicit lookup semantics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given find helpers for package, phase, and build-step lookup
When lookup is performed
Then multiple matches raise a ``ValueError``
And missing values raise ``ValueError`` by default
And optional ``raise_if_not_found=false`` returns ``None`` for missing values.

History Persistence
-------------------

Scenario: History directory initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given ``HistoryFileManager`` initialization
When the configured history path does not exist
Then the directory is created recursively.

Scenario: Build-step history file format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a successful build-step execution
When it is added to history
Then it is serialized as a single-build-step ``PackageFile`` YAML document
And written to a file named exactly as the build-step name.

Scenario: Duplicate history writes are rejected
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given an existing build-step history file with the same name
When writing history for that build step
Then a ``ValueError`` is raised.

Scenario: Reading previous build steps from history
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given existing history files
When previous build steps are loaded
Then each file is deserialized and validated as a ``PackageFile``
And each history file must contain exactly one build step.

Serialization
-------------

Scenario: YAML serialization for package models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a package-file model
When serialized to YAML
Then model dumping uses JSON mode for path compatibility
And keys are emitted without alphabetical sorting
And ``None`` fields are excluded from output.
