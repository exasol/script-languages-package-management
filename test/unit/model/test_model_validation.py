import re

import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    PPA,
    AptPackage,
    Bazel,
    Micromamba,
    PackageFile,
    Pip,
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
                  -  name: some_ppa
                     key_server: http://some_key_server
                     key: some_key
                     ppa: deb http://some_ppa_server/some_ppa some_ppa/
                     out_file: some_out_file
                     comment: This is a sample PPA
                  -  name: some_other_ppa
                     key_server: http://some_key_server
                     key: some_other_key
                     ppa: deb http://some_other_ppa_server/some_ppa some_ppa/
                     out_file: some_other_out_file
                     comment: This is a sample PPA
                packages:
                - name: curl
                  version: 7.68.0
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    expected_first_ppa = PPA(
        name="some_ppa",
        key_server="http://some_key_server",
        key="some_key",
        ppa="deb http://some_ppa_server/some_ppa some_ppa/",
        out_file="some_out_file",
        comment="This is a sample PPA",
    )
    expected_second_ppa = PPA(
        name="some_other_ppa",
        key_server="http://some_key_server",
        key="some_other_key",
        ppa="deb http://some_other_ppa_server/some_ppa some_ppa/",
        out_file="some_other_out_file",
        comment="This is a sample PPA",
    )
    assert model
    assert model.find_build_step("build_step_one").find_phase("phase_one").apt.ppas == [
        expected_first_ppa,
        expected_second_ppa,
    ]


def test_unique_ppa():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            apt:
                ppas:
                  -  name: some_ppa
                     key_server: http://some_key_server
                     key: some_key
                     ppa: deb http://some_ppa_server/some_ppa some_ppa/
                     out_file: some_out_file
                     comment: This is a sample PPA
                  -  name: some_other_ppa
                     key_server: http://some_key_server
                     key: some_key
                     ppa: deb http://some_other_ppa_server/some_ppa some_ppa/
                     out_file: some_other_out_file
                     comment: This is a sample PPA
                packages:
                - name: curl
                  version: 7.68.0
    """
    yaml_data = yaml.safe_load(yaml_file)
    expected_error = "PPA's must be unique. Multiple PPA's with same key were detected: (['some_ppa', 'some_other_ppa']) at [<PackageFile root> -> <Build-Step 'build_step_one'> -> <Phase 'phase_one'>]"
    with pytest.raises(PackageFileValidationError, match=re.escape(expected_error)):
        PackageFile.model_validate(yaml_data)


def test_valid_package_installer_pip():
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
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model


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


def test_valid_package_installer_conda():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            
            conda:
                channels: null
                comment: null
                packages:
                - name: numpy
                  version: 1.19.2
                  comment: install numpy
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model


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
                    comment: install pip
                micromamba:
                    version: 1.2.3
                    comment: install micromamba
                bazel:
                    version: 1.2.3
                    comment: install bazel
                python_binary_path: /usr/bin/python3.12
                r_binary_path: /usr/bin/r4.4

            apt:
                packages:
                - name: curl
                  version: 7.68.0
                  comment: install curl
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model
    assert model.find_build_step("build_step_one").find_phase(
        "phase_one"
    ).tools == Tools(
        pip=Pip(version="1.2.3", comment="install pip"),
        micromamba=Micromamba(version="1.2.3", comment="install micromamba"),
        bazel=Bazel(version="1.2.3", comment="install bazel"),
        python_binary_path="/usr/bin/python3.12",
        r_binary_path="/usr/bin/r4.4",
    )


def test_variables():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:

          - name: phase_one
            comment: null
            apt:
                packages:
                - name: curl
                  version: 7.68.0
                  comment: install curl
            variables:
                java_home: /usr/java
                python_prefix: /usr/bin/
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model
    assert model.find_build_step("build_step_one").find_phase(
        "phase_one"
    ).variables == {"java_home": "/usr/java", "python_prefix": "/usr/bin/"}


def test_valid_package_all_installers():
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
        
          - name: phase_one
            comment: null
            r:
                comment: null
                packages:
                - name: ggplot2
                  version: 3.3.5
                  comment: install ggplot
                  
            apt:
                packages:
                - name: curl
                  version: 7.68.0
                  comment: install curl
            conda:
                channels: null
                comment: null
                packages:
                - name: numpy
                  version: 1.19.2
                  comment: install numpy
            pip:
                packages:
                - name: requests
                  version: 2.25.1
                  comment: install requests
    """
    yaml_data = yaml.safe_load(yaml_file)
    model = PackageFile.model_validate(yaml_data)
    assert model
