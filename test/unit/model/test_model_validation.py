import re

import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    PackageFile,
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
