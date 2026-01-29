# tests/test_to_yaml_str.py
from pathlib import Path

import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    PackageFile,
    Phase,
    Tools,
)
from exasol.exaslpm.model.serialization import to_yaml_str  # adjust import


def test_to_yaml_str_roundtrip_preserves_structure_and_values():
    model = PackageFile.model_validate(
        {
            "version": "1.0.0",
            "build_steps": [
                {
                    "name": "build",
                    "phases": [
                        {
                            "name": "phase1",
                            "variables": {"A": "1"},
                            "pip": {
                                "packages": [
                                    {"name": "requests", "version": "2.31.0"},
                                ]
                            },
                        }
                    ],
                }
            ],
        }
    )

    yml = to_yaml_str(model)
    data = yaml.safe_load(yml)

    assert PackageFile.model_validate(data) == model


def test_to_yaml_str_serializes_paths_as_strings():
    model = PackageFile(
        version="1.0.0",
        comment="c",
        build_steps=[
            BuildStep(
                name="build-step-1",
                phases=[
                    Phase(
                        name="phase1",
                        tools=Tools(python_binary_path=Path("/usr/bin/python3")),
                    )
                ],
            )
        ],
    )
    yml = to_yaml_str(model)
    data = yaml.safe_load(yml)

    python_path = data["build_steps"][0]["phases"][0]["tools"]["python_binary_path"]
    assert python_path == "/usr/bin/python3"
    assert isinstance(python_path, str)


def test_to_yaml_str_omits_none_fields_by_default_in_dump():
    # model_dump(mode="json") includes None fields by default.
    # to_yaml_str() sets exclude_none=True
    # Validate that None fields are not included in resulting yaml
    model = PackageFile(
        version="1.0.0",
        comment="c",
        build_steps=[
            BuildStep(
                name="build-step-1",
                phases=[
                    Phase(
                        name="phase1",
                        apt=AptPackages(
                            packages=[AptPackage(name="requests", version="2.31.0")]
                        ),
                    )
                ],
            )
        ],
    )

    yml = to_yaml_str(model)
    data = yaml.safe_load(yml)

    phase = data["build_steps"][0]["phases"][0]
    assert "apt" in phase
    # Ensure optional sections not provided are not forced into YAML
    assert "pip" not in phase
    assert "r" not in phase
    assert "conde" not in phase
    assert "tools" not in phase
    assert "variables" not in phase


def test_to_yaml_str_produces_valid_yaml_for_empty_lists_and_nested_models():
    model = PackageFile.model_validate(
        {
            "version": "1.0.0",
            "build_steps": [
                {
                    "name": "build",
                    "phases": [
                        {
                            "name": "phase1",
                            "conda": {
                                "packages": [],
                                "channels": None,
                                "binary": "Micromamba",
                            },
                        }
                    ],
                }
            ],
        }
    )

    yml = to_yaml_str(model)
    # Should be parseable YAML
    data = yaml.safe_load(yml)

    assert data["build_steps"][0]["phases"][0]["conda"]["packages"] == []


@pytest.mark.parametrize(
    "bad_model",
    [
        None,
        "not-a-model",
        123,
        {"build_steps": []},
    ],
)
def test_to_yaml_str_rejects_non_packagefile_objects(bad_model):
    with pytest.raises(AttributeError):
        to_yaml_str(bad_model)  # type: ignore[arg-type]
