import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    BuildStep,
    PackageFile,
    Phase,
)


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
    with pytest.raises(ValueError) as excinfo:
        PackageFile.model_validate(yaml_data)
    assert "at least one Buildstep" in str(excinfo.value)


def test_empty_package_file_without_comment():
    yaml_file = """
        build_steps: []
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(ValueError) as excinfo:
        PackageFile.model_validate(yaml_data)
    assert "at least one Buildstep" in str(excinfo.value)


def test_empty_build_step():
    yaml_file = """
        name: build_step_one
        phases: []
        comment: null
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(ValueError) as excinfo:
        BuildStep.model_validate(yaml_data)
    assert "at least one Phase" in str(excinfo.value)


def test_empty_package_installer():
    yaml_file = """
        name: phase_one
        apt: null
        pip: null
        r: null
        conda: null
        comment: null
    """
    yaml_data = yaml.safe_load(yaml_file)
    with pytest.raises(ValueError) as excinfo:
        Phase.model_validate(yaml_data)
    assert "at least one Package installer" in str(excinfo.value)


def test_valid_package_installer_apt():
    yaml_file = """
    name: phase_one
    apt:
        packages:
        - name: curl
          version: 7.68.0
          comment: install curl
    """
    yaml_data = yaml.safe_load(yaml_file)
    phase = Phase.model_validate(yaml_data)
    assert phase


def test_valid_package_installer_apt_without_comment():
    yaml_file = """
    name: phase_one
    apt:
        packages:
        - name: curl
          version: 7.68.0
    """
    yaml_data = yaml.safe_load(yaml_file)
    phase = Phase.model_validate(yaml_data)
    assert phase


def test_valid_package_installer_pip():
    yaml_file = """
    name: phase_one
    pip:
        packages:
        - name: requests
          version: 2.25.1
          comment: install requests
    """
    yaml_data = yaml.safe_load(yaml_file)
    phase = Phase.model_validate(yaml_data)
    assert phase


def test_valid_package_installer_conda():
    yaml_file = """
    name: phase_one
    
    conda:
        channels: null
        comment: null
        packages:
        - name: numpy
          version: 1.19.2
          comment: install numpy
    """
    yaml_data = yaml.safe_load(yaml_file)
    phase = Phase.model_validate(yaml_data)
    assert phase


def test_valid_package_installer_r():
    yaml_file = """
    name: phase_one
    
    r:
        comment: null
        packages:
        - name: ggplot2
          version: 3.3.5
          comment: install ggplot
    """
    yaml_data = yaml.safe_load(yaml_file)
    phase = Phase.model_validate(yaml_data)
    assert phase


def test_valid_package_installer_r_without_comment():
    yaml_file = """
    name: phase_one
    r:
        comment: null
        packages:
        - name: ggplot2
          version: 3.3.5
    """
    yaml_data = yaml.safe_load(yaml_file)
    phase = Phase.model_validate(yaml_data)
    assert phase


def test_valid_package_all_installers():
    yaml_file = """
    name: phase_one
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
    phase = Phase.model_validate(yaml_data)
    assert phase
