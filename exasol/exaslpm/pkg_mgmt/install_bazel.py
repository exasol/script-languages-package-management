import platform
import stat
from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    Phase,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context


def install_bazel(phase: Phase, ctx: Context):
    if phase.tools and phase.tools.bazel:
        bazel = phase.tools.bazel
        bazel_machine_mapping = {"x86_64": "x86_64", "aarch64": "arm64"}
        bazel_machine = bazel_machine_mapping[platform.machine()]
        url = f"https://github.com/bazelbuild/bazel/releases/download/{bazel.version}/bazel-{bazel.version}-linux-{bazel_machine}"
        with ctx.file_downloader.download_file_to_tmp(
            url=url
        ) as get_bazel:
            ctx.file_access.chmod(get_bazel, stat.S_IXUSR)
            ctx.file_access.copy_file(get_bazel, Path("/usr/bin/bazel"))
