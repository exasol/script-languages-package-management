import json
from test.unit.test_data import (
    TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_APT,
    TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_CONDA,
    TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_PIP,
    TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_R,
)
from unittest.mock import (
    MagicMock,
    call,
)

import pytest

from exasol.exaslpm.model.installed_packages_config import InstalledPackages
from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    CondaPackage,
    PipPackage,
    RPackage,
)
from exasol.exaslpm.pkg_mgmt.list_all_installed_packages import (
    list_all_installed_packages,
)


def test_get_installed_packages_empty_history(context_mock) -> None:
    installed_packages = list_all_installed_packages(context_mock)
    assert installed_packages == InstalledPackages()


@pytest.mark.parametrize(
    "build_step, stdout_str, expected_call, expected_packages",
    [
        (
            TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_APT,
            "curl,7.68.0",
            call.execute(["dpkg-query", "-W", "-f=${Package},${Version}\n"]),
            InstalledPackages(
                apt=[AptPackage(name="curl", version="7.68.0", comment=None)]
            ),
        ),
        (
            TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_PIP,
            json.dumps([{"name": "pydantic", "version": "2.13.4"}]),
            call.execute(
                ["python3", "-m", "pip", "list", "--format", "json", "--no-cache-dir"]
            ),
            InstalledPackages(
                pip=[PipPackage(name="pydantic", version="2.13.4", comment=None)]
            ),
        ),
        (
            TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_R,
            "poorman,0.2.7",
            call.execute(
                [
                    "Rscript",
                    "-e",
                    'write.table(installed.packages()[,c("Package","Version")], sep=",", row.names=FALSE, col.names=FALSE)',
                ]
            ),
            InstalledPackages(
                r=[RPackage(name="poorman", version="0.2.7", comment=None)]
            ),
        ),
        (
            TEST_BUILD_STEP_LIST_ALL_INSTALLED_PACKAGES_CONDA,
            json.dumps(
                [{"name": "zstd", "version": "1.5.7", "channel": "conda-forge"}]
            ),
            call.execute(["/bin/micromamba", "list", "--json"]),
            InstalledPackages(
                conda=[
                    CondaPackage(
                        name="zstd",
                        version="1.5.7",
                        channel="conda-forge",
                        comment=None,
                    )
                ]
            ),
        ),
    ],
)
def test_get_installed_packages_success(
    context_mock, build_step, stdout_str, expected_call, expected_packages
) -> None:
    context_mock.history_file_manager.build_steps = [build_step]

    execute_ret = MagicMock()
    context_mock.cmd_executor.execute.return_value = execute_ret

    def consume_results_side_effect(stdout_cb, _):
        stdout_cb(stdout_str)
        return 0

    execute_ret.consume_results.side_effect = consume_results_side_effect

    packages = list_all_installed_packages(context_mock)

    assert context_mock.cmd_executor.mock_calls[0] == expected_call
    assert packages == expected_packages
