from exasol.exaslpm.model.package_file_config import (
    Phase,
    RPackage,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache

INSTALL_METHOD = """
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
"""

VALIDATE_METHOD = """

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
"""


def _prepare_remotes_library(search_cache: SearchCache, context: Context):
    '$rscript_binary -e \'install.packages("remotes",repos="https://cloud.r-project.org")\' '
    cmd = CommandExecInfo(
        cmd=[
            str(search_cache.r_binary_path),
            "-e",
            'install.packages("remotes",repos="https://cloud.r-project.org")',
        ],
        err="Error during installation of remotes library.",
    )
    run_cmd(cmd, context)


def _add_r_function_call_for_pkg(function_call: str, pkg: RPackage) -> str:
    version_str = f'"{pkg.version}"' if pkg.version else "NULL"
    pkg_str = f'"{pkg.name}"'
    return f"{function_call}({pkg_str},{version_str})"


def _install_r_function_call(pkg: RPackage) -> str:
    return _add_r_function_call_for_pkg("install_or_fail", pkg)


def _validate_r_function_call(pkg: RPackage) -> str:
    return _add_r_function_call_for_pkg("validate_or_fail", pkg)


def _install_packages(
    packages: list[RPackage], search_cache: SearchCache, context: Context
):
    with context.temp_file_provider.create() as temp_file:
        with temp_file.open() as f:
            print(INSTALL_METHOD, file=f)
            for pkg in packages:
                print(_install_r_function_call(pkg), file=f)

        cmd = CommandExecInfo(
            cmd=[str(search_cache.r_binary_path), str(temp_file.path)],
            err="Error during installation of R packages.",
        )
        run_cmd(cmd, context)


def _validate_packages(
    packages: list[RPackage], search_cache: SearchCache, context: Context
):
    with context.temp_file_provider.create() as temp_file:
        with temp_file.open() as f:
            print(VALIDATE_METHOD, file=f)
            for pkg in packages:
                print(_validate_r_function_call(pkg), file=f)

        cmd = CommandExecInfo(
            cmd=[str(search_cache.r_binary_path), str(temp_file.path)],
            err="Error during validation of R packages.",
        )
        run_cmd(cmd, context)


def install_r(search_cache: SearchCache, phase: Phase, context: Context):
    if phase.r and phase.r.packages:
        _prepare_remotes_library(search_cache, context)
        _install_packages(phase.r.packages, search_cache, context)
        _validate_packages(phase.r.packages, search_cache, context)
    else:
        context.cmd_logger.warn("Got an empty list of R packages")
