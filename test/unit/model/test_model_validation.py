import itertools
import re
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from exasol.exaslpm.model.package_file_config import (
    PPA,
    AptPackage,
    Bazel,
    CondaBinary,
    Micromamba,
    PackageFile,
    Pip,
    PipPackage,
    Tools,
)
from exasol.exaslpm.model.package_validation_error import PackageFileValidationError


def test_package_item():
    yaml_file = """
            name: numpy
            version: 1.19.2
        """
    yaml_data = yaml.safe_load(yaml_file)
    pkg = AptPackage.model_validate(yaml_data)
    assert pkg is not None


def test_empty_package_file_with_comment():
    yaml_file = """
        build_steps: []
        comment: null
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(
        PackageFileValidationError,
        match=re.escape("at least one Buildstep at [<PackageFile root>]"),
    ):
        PackageFile.model_validate(yaml_data)


def test_unique_build_step_names():
    yaml_file = """
        build_steps:
            - name: build_step_one
              phases:
                - name: phase 1
                  apt:
                    packages:
                      - name: "curl"
                        version: "7.68.0"
                        comment: "For downloading"
            - name: build_step_one
              phases:
                - name: phase 1
                  apt:
                    packages:
                      - name: "curl"
                        version: "7.68.0"
                        comment: "For downloading"
        comment: null
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(
        PackageFileValidationError,
        match=re.escape(
            "Buildstep names must be unique. Multiple Buildsteps were detected: (['build_step_one']) at [<PackageFile root>]"
        ),
    ):
        PackageFile.model_validate(yaml_data)


def test_empty_package_file_without_comment():
    yaml_file = """
        build_steps: []
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(
        PackageFileValidationError,
        match=re.escape(
            "There shall be at least one Buildstep at [<PackageFile root>]"
        ),
    ):
        PackageFile.model_validate(yaml_data)


def test_empty_build_step():
    yaml_file = """
        build_steps:
            - name: build_step_one
              phases: []
              comment: null
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(
        PackageFileValidationError,
        match=re.escape(
            "There shall be at least one Phase at [<PackageFile root> -> <Build-Step 'build_step_one'>]"
        ),
    ):
        PackageFile.model_validate(yaml_data)


def test_unique_phase_names():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase 1
            apt:
              packages:
                - name: "curl"
                  version: "7.68.0"
                  comment: "For downloading"
          - name: phase 1
            apt:
              packages:
                - name: "curl"
                  version: "7.68.0"
                  comment: "For downloading"
        comment: null
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(
        PackageFileValidationError,
        match=re.escape(
            "Phase names must be unique. Multiple phases were detected: (['phase 1']) at [<PackageFile root> -> <Build-Step 'build_step_one'>]"
        ),
    ):
        PackageFile.model_validate(yaml_data)


def test_empty_package_installer():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            apt: null
            pip: null
            r: null
            conda: null
            comment: null
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(
        PackageFileValidationError,
        match=re.escape(
            "There shall be at least one Package installer at [<PackageFile root> -> <Build-Step 'build_step_one'> -> <Phase 'phase_one'>]"
        ),
    ):
        PackageFile.model_validate(yaml_data)


def test_valid_package_installer_apt():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            apt:
                packages:
                - name: curl
                  version: 7.68.0
                  comment: install curl
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model


def test_valid_package_installer_apt_without_comment():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            apt:
                packages:
                - name: curl
                  version: 7.68.0
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model


def test_unique_apt_packages():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            apt:
                comment: null
                packages:
                - name: curl
                  version: 7.68.0
                - name: curl
                  version: 7.42.0
    """
    yaml_data = yaml.safe_load(yaml_file)
    expected_error = "Packages must be unique. Multiple packages were detected: (['curl']) at [<PackageFile root> -> <Build-Step 'build_step_one'> -> <Phase 'phase_one'> -> <AptPackages>]"
    with pytest.raises(PackageFileValidationError, match=re.escape(expected_error)):
        PackageFile.model_validate(yaml_data)


def test_ppa():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            apt:
                ppas:
                  some_ppa:
                     key_url: http://some_key_server
                     apt_repo_entry: deb http://some_ppa_server/some_ppa some_ppa/
                     out_file: some_out_file
                     comment: This is a sample PPA
                  some_other_ppa:
                     key_url: http://some_key_server
                     apt_repo_entry: deb http://some_other_ppa_server/some_ppa some_ppa/
                     out_file: some_other_out_file
                     comment: This is a sample PPA
                packages:
                - name: curl
                  version: 7.68.0
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    expected_first_ppa = PPA(
        key_url="http://some_key_server",
        key_fingerprint="some_key",
        apt_repo_entry="deb http://some_ppa_server/some_ppa some_ppa/",
        out_file="some_out_file",
        comment="This is a sample PPA",
    )
    expected_second_ppa = PPA(
        key_url="http://some_key_server",
        key_fingerprint="some_other_key",
        apt_repo_entry="deb http://some_other_ppa_server/some_ppa some_ppa/",
        out_file="some_other_out_file",
        comment="This is a sample PPA",
    )
    assert model
    assert model.find_build_step("build_step_one").find_phase("phase_one").apt.ppas == {
        "some_ppa": expected_first_ppa,
        "some_other_ppa": expected_second_ppa,
    }


def test_valid_package_installer_pip_name():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            pip:
                packages:
                - name: requests
                  version: 2.25.1
                  comment: install requests
                install_build_tools_ephemerally: True
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model
    pip = model.find_build_step("build_step_one").find_phase("phase_one").pip

    assert pip.packages == [
        PipPackage(name="requests", version="2.25.1", comment="install requests")
    ]
    assert pip.install_build_tools_ephemerally is True


def test_valid_package_installer_pip_url():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            pip:
                packages:
                - name: some_package
                  url: http://some_package
                  version: 2.25.1
                  comment: some package
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model
    pip = model.find_build_step("build_step_one").find_phase("phase_one").pip

    assert pip.packages == [
        PipPackage(
            name="some_package",
            url="http://some_package",
            version="2.25.1",
            comment="some package",
        )
    ]


def test_unique_pip_packages():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            pip:
                comment: null
                packages:
                - name: requests
                  version: 2.25.1
                  comment: install requests
                - name: requests
                  version: 2.5.1
    """
    yaml_data = yaml.safe_load(yaml_file)
    expected_error = "Packages must be unique. Multiple packages were detected: (['requests']) at [<PackageFile root> -> <Build-Step 'build_step_one'> -> <Phase 'phase_one'> -> <PipPackages>]"
    with pytest.raises(PackageFileValidationError, match=re.escape(expected_error)):
        PackageFile.model_validate(yaml_data)


@pytest.mark.parametrize(
    "conda_binary",
    [CondaBinary.Micromamba.value, CondaBinary.Mamba.value, CondaBinary.Conda.value],
)
def test_valid_package_installer_conda(conda_binary):
    yaml_file = f"""
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            
            conda:
                channels: null
                binary: {conda_binary}
                comment: null
                packages:
                - name: numpy
                  version: 1.19.2
                  comment: install numpy
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model


def test_valid_package_installer_conda_invalid_binary():
    yaml_file = f"""
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one

            conda:
                channels: null
                binary: invalid_conda_binary
                comment: null
                packages:
                - name: numpy
                  version: 1.19.2
                  comment: install numpy
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(
        ValidationError, match=r"Input should be 'Micromamba', 'Mamba' or 'Conda'"
    ):
        PackageFile.model_validate(yaml_data)


def test_unique_conda_packages():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            conda:
                comment: null
                packages:
                - name: numpy
                  version: 1.19.2
                  comment: install numpy
                - name: numpy
                  version: 1.2.0
    """
    yaml_data = yaml.safe_load(yaml_file)
    expected_error = "Packages must be unique. Multiple packages were detected: (['numpy']) at [<PackageFile root> -> <Build-Step 'build_step_one'> -> <Phase 'phase_one'> -> <CondaPackages>]"
    with pytest.raises(PackageFileValidationError, match=re.escape(expected_error)):
        PackageFile.model_validate(yaml_data)


def test_valid_package_installer_r():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one            
            r:
                comment: null
                packages:
                - name: ggplot2
                  version: 3.3.5
                  comment: install ggplot
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model


def test_valid_package_installer_r_without_comment():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            r:
                comment: null
                packages:
                - name: ggplot2
                  version: 3.3.5
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model


def test_unique_r_packages():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            r:
                comment: null
                packages:
                - name: ggplot2
                  version: 3.3.5
                - name: ggplot2
                  version: 1.2.3
    """
    yaml_data = yaml.safe_load(yaml_file)
    expected_error = "Packages must be unique. Multiple packages were detected: (['ggplot2']) at [<PackageFile root> -> <Build-Step 'build_step_one'> -> <Phase 'phase_one'> -> <RPackages>]"
    with pytest.raises(PackageFileValidationError, match=re.escape(expected_error)):
        PackageFile.model_validate(yaml_data)


def test_tools():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            tools:
                pip:
                    version: 1.2.3
                    needs_break_system_packages: true
                    comment: install pip
                micromamba:
                    version: 1.2.3
                    root_prefix: /some/path
                    comment: install micromamba
                bazel:
                    version: 1.2.3
                    comment: install bazel
                python_binary_path: /usr/bin/python3.12
                r_binary_path: /usr/bin/r4.4
                conda_binary_path: /usr/conda/bin/conda
                mamba_binary_path: /usr/conda/bin/mamba
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model
    assert model.find_build_step("build_step_one").find_phase(
        "phase_one"
    ).tools == Tools(
        pip=Pip(
            version="1.2.3", needs_break_system_packages=True, comment="install pip"
        ),
        micromamba=Micromamba(
            version="1.2.3",
            comment="install micromamba",
            root_prefix=Path("/some/path"),
        ),
        bazel=Bazel(version="1.2.3", comment="install bazel"),
        python_binary_path=Path("/usr/bin/python3.12"),
        r_binary_path=Path("/usr/bin/r4.4"),
        conda_binary_path=Path("/usr/conda/bin/conda"),
        mamba_binary_path=Path("/usr/conda/bin/mamba"),
    )


R_PACKAGES_DATA = """
            r:
                comment: null
                packages:
                - name: ggplot2
                  version: 3.3.5
                  comment: install ggplot
"""

CONDA_PACKAGES_DATA = """
            conda:
                channels: null
                comment: null
                packages:
                - name: numpy
                  version: 1.19.2
                  comment: install numpy
"""

PIP_PACKAGES_DATA = """
            pip:
                packages:
                - name: requests
                  version: 2.25.1
                  comment: install requests

"""

APT_PACKAGES_DATA = """
            apt:
                packages:
                - name: curl
                  version: 7.68.0
                  comment: install curl
"""

TOOLS_DATA = """
            tools:
                python_binary_path: /some/path
"""


@pytest.mark.parametrize(
    "additional_entry",
    [
        "",
        R_PACKAGES_DATA,
        APT_PACKAGES_DATA,
        TOOLS_DATA,
        CONDA_PACKAGES_DATA,
        PIP_PACKAGES_DATA,
    ],
)
def test_variables(additional_entry):
    base_yaml_file = """
    build_steps:
      - name: build_step_one
        phases:

          - name: phase_one
            comment: null
            variables:
                java_home: /usr/java
                python_prefix: /usr/bin/
    """
    yaml_file = base_yaml_file + additional_entry
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model
    assert model.find_build_step("build_step_one").find_phase(
        "phase_one"
    ).variables == {"java_home": "/usr/java", "python_prefix": "/usr/bin/"}


def build_phase_entries() -> Iterator[list[str]]:
    """
    Returns an Iterator for all combinations of all phase entries with length >=2:
    - [R_PACKAGES_DATA, APT_PACKAGES_DATA]
    - [R_PACKAGES_DATA, PIP_PACKAGES_DATA]
    - [R_PACKAGES_DATA, CONDA_PACKAGES_DATA]
    - [APT_PACKAGES_DATA, PIP_PACKAGES_DATA]
    - ...
    - [R_PACKAGES_DATA, APT_PACKAGES_DATA, PIP_PACKAGES_DATA]
    - [R_PACKAGES_DATA, APT_PACKAGES_DATA, CONDA_PACKAGES_DATA]
    - ...
    - [R_PACKAGES_DATA, APT_PACKAGES_DATA, PIP_PACKAGES_DATA, CONDA_PACKAGES_DATA]
    - ...
    - [R_PACKAGES_DATA, APT_PACKAGES_DATA, PIP_PACKAGES_DATA, CONDA_PACKAGES_DATA, TOOLS_DATA]

    """
    all_phase_entries = [
        R_PACKAGES_DATA,
        APT_PACKAGES_DATA,
        PIP_PACKAGES_DATA,
        CONDA_PACKAGES_DATA,
        TOOLS_DATA,
    ]
    min_length = 2
    max_length = len(all_phase_entries)
    for length in range(min_length, max_length + 1):
        combinations_object = itertools.combinations(all_phase_entries, length)
        # Convert combinations (tuples) to lists and extend the main list
        for combo in combinations_object:
            yield list(combo)


@pytest.mark.parametrize("phase_entries", build_phase_entries())
def test_valid_package_all_installers(phase_entries):
    base_yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
        
          - name: phase_one
            comment: null
    """
    yaml_file = base_yaml_file + "\n".join(phase_entries)
    yaml_data = yaml.safe_load(yaml_file)

    with pytest.raises(
        PackageFileValidationError,
        match=r"A phase must have exactly one of: apt, pip, conda, r, tools.",
    ):
        PackageFile.model_validate(yaml_data)


R_PACKAGES_NO_VERSION_DATA = """
            r:
                comment: null
                packages:
                - name: ggplot2
                  comment: install ggplot
"""

CONDA_PACKAGES_NO_VERSION_DATA = """
            conda:
                channels: null
                comment: null
                packages:
                - name: numpy
                  comment: install numpy
"""

PIP_PACKAGES_NO_VERSION_DATA = """
            pip:
                packages:
                - name: requests
                  comment: install requests

"""

APT_PACKAGES_NO_VERSION_DATA = """
            apt:
                packages:
                - name: curl
                  comment: install curl
"""


@pytest.mark.parametrize(
    "package_data",
    [
        R_PACKAGES_NO_VERSION_DATA,
        APT_PACKAGES_NO_VERSION_DATA,
        CONDA_PACKAGES_NO_VERSION_DATA,
        PIP_PACKAGES_NO_VERSION_DATA,
    ],
    ids=["R", "APT", "CONDA", "PIP"],
)
def test_no_version(package_data):
    base_yaml_file = """
    build_steps:
      - name: build_step_one
        validation_cfg:
          version_mandatory: false          
        phases:
          - name: phase_one
            comment: null
    """
    yaml_file = base_yaml_file + package_data
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model


@pytest.mark.parametrize(
    "package_data",
    [
        R_PACKAGES_NO_VERSION_DATA,
        APT_PACKAGES_NO_VERSION_DATA,
        CONDA_PACKAGES_NO_VERSION_DATA,
        PIP_PACKAGES_NO_VERSION_DATA,
    ],
    ids=["R", "APT", "CONDA", "PIP"],
)
def test_no_version_raises(package_data):
    base_yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            comment: null
    """
    yaml_file = base_yaml_file + package_data
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(
        PackageFileValidationError,
        match=re.escape(r"Package(s) without version found"),
    ):
        PackageFile.model_validate(yaml_data)


def test_pip_package_with_url_and_no_version():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            comment: null
            pip:
                packages:
                - name: requests
                  url: https://pypi.org/requests
                  comment: install requests
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model
    assert model.find_build_step("build_step_one").find_phase(
        "phase_one"
    ).pip.packages == [
        PipPackage(
            name="requests",
            url="https://pypi.org/requests",
            version=None,
            comment="install requests",
        )
    ]
