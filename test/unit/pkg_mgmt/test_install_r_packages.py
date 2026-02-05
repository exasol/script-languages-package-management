from pathlib import Path
from unittest.mock import (
    call,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
    RPackage,
    RPackages,
    Tools,
)
from exasol.exaslpm.pkg_mgmt.install_r_packages import (
    _install_packages,
    _validate_packages,
    install_r_packages,
)
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


@pytest.fixture
def context_with_r_env(context_mock):
    phase_r_binary = Phase(
        name="phase-r-bin",
        tools=Tools(r_binary_path=Path("/usr/bin/Rscript")),
    )
    context_mock.history_file_manager.build_steps = [
        BuildStep(name="prev-build-step", phases=[phase_r_binary])
    ]
    return context_mock


def test_empty_packages(context_with_r_env):
    rPackages = RPackages(packages=[])
    phase_one = Phase(name="phase-1", r=rPackages)
    build_step = BuildStep(name="build-step-1", phases=[phase_one])
    search_cache = SearchCache(build_step, phase_one, context_with_r_env)
    install_r_packages(search_cache, phase_one, context_with_r_env)

    assert context_with_r_env.cmd_logger.mock_calls == [
        call.warn("Got an empty list of R packages"),
    ]


TEST_PACKAGES = [
    RPackage(name="tidyr", version="1.3.2"),
    RPackage(name="dplyr", version="1.2.0"),
]


def _make_build_step() -> BuildStep:
    rPackages = RPackages(packages=TEST_PACKAGES)
    phase_one = Phase(name="phase-1", r=rPackages)
    build_step = BuildStep(name="build-step-1", phases=[phase_one])
    return build_step


def test_install_r_packages(context_with_r_env):
    build_step = _make_build_step()
    phase = build_step.find_phase("phase-1")
    search_cache = SearchCache(build_step, phase, context_with_r_env)
    install_r_packages(search_cache, phase, context_with_r_env)
    assert context_with_r_env.cmd_executor.mock_calls == [
        call.execute(
            [
                "/usr/bin/Rscript",
                "-e",
                'install.packages("remotes",repos="https://cloud.r-project.org")',
            ],
            env=None,
        ),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["/usr/bin/Rscript", "path/to/temp/file"], env=None),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["/usr/bin/Rscript", "path/to/temp/file"], env=None),
        call.execute().print_results(),
        call.execute().return_code(),
    ]


def test_install_r_packages_script(context_with_r_env):
    build_step = _make_build_step()
    phase = build_step.find_phase("phase-1")
    search_cache = SearchCache(build_step, phase, context_with_r_env)
    _install_packages(TEST_PACKAGES, search_cache, context_with_r_env)

    expected_install_script = """
library(remotes)
install_or_fail <- function(package_name, version){

   tryCatch({install_version(package_name, version, repos="https://cloud.r-project.org", Ncpus=4, upgrade="never")
         library(package_name, character.only = TRUE)},
         error = function(e){
             print(e)
             stop(paste("installation failed for:",package_name ))},
         warning = function(w){
           catch <-
             grepl("download of package .* failed", w$message) ||
             grepl("(dependenc|package).*(is|are) not available", w$message) ||
             grepl("installation of package.*had non-zero exit status", w$message) ||
             grepl("installation of one or more packages failed", w$message)
           if(catch){ print(w$message)
             stop(paste("installation failed for:",package_name ))}}
         )

 }

install_or_fail("tidyr","1.3.2")
install_or_fail("dplyr","1.2.0")
"""
    assert context_with_r_env.temp_file_provider.result == expected_install_script
    assert context_with_r_env.cmd_executor.mock_calls == [
        call.execute(["/usr/bin/Rscript", "path/to/temp/file"], env=None),
        call.execute().print_results(),
        call.execute().return_code(),
    ]


def test_validate_r_packages_script(context_with_r_env):
    build_step = _make_build_step()
    phase = build_step.find_phase("phase-1")
    search_cache = SearchCache(build_step, phase, context_with_r_env)
    _validate_packages(TEST_PACKAGES, search_cache, context_with_r_env)

    expected_validate_script = """
library(remotes)
installed_packages <- installed.packages()
installed_package_names <- installed_packages[, "Package"]

validate_or_fail <- function(package_name, version){
    # Check if the package is in the list of available packages
    is_installed <- package_name %in% installed_package_names

    # Check the result
    if (!is_installed) {
        stop(paste("Package not installed:", package_name))
    }

    if (!is.null(version)) {
       desc <- packageDescription(package_name)
       if (version != desc$Version) {
        stop(paste("Version of  installed installed package does not match:", package_name))
       }
    }
}

validate_or_fail("tidyr","1.3.2")
validate_or_fail("dplyr","1.2.0")
"""
    assert context_with_r_env.temp_file_provider.result == expected_validate_script
    assert context_with_r_env.cmd_executor.mock_calls == [
        call.execute(["/usr/bin/Rscript", "path/to/temp/file"], env=None),
        call.execute().print_results(),
        call.execute().return_code(),
    ]
