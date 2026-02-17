import csv
from dataclasses import dataclass
from io import StringIO
from typing import Any

from exasol.exaslpm.model.package_file_config import AptPackage
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.context.context import Context

"""
This is how the apt-cache madison output looks
apt-cache madison gpg vim
gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
gpg | 2.4.4-2ubuntu17.4 | http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
gpg | 2.4.4-2ubuntu17 | http://archive.ubuntu.com/ubuntu noble/main amd64 Packages
vim | 2:9.1.0016-1ubuntu7.9 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
vim | 2:9.1.0016-1ubuntu7.9 | http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
vim | 2:9.1.0016-1ubuntu7 | http://archive.ubuntu.com/ubuntu noble/main amd64 Packages
"""


@dataclass
class MadisonData:
    ver: str
    tail: str


class MadisonExecutor:
    @staticmethod
    def execute_madison(pkg_list: list[AptPackage], ctx: Context) -> str:
        if not pkg_list:
            return ""
        cmd = ["apt-cache", "madison"]
        for pkg in pkg_list:
            cmd.append(pkg.name)
        cmd_res = ctx.cmd_executor.execute(cmd)

        stdout_lines: list[str] = []

        def consume_stdout(line: str | bytes, _ctx: Any) -> None:
            if isinstance(line, bytes):
                line = line.decode()
            stdout_lines.append(line)

        def consume_stderr(_line: str | bytes, _ctx: Any) -> None:
            pass

        ret_code = cmd_res.consume_results(consume_stdout, consume_stderr)
        if ret_code != 0:
            raise CommandFailedException("Failed executing madison")
        return " ".join(stdout_lines)


class MadisonParser:
    @staticmethod
    def parse_madison_output(madison_out: str) -> dict[str, list[MadisonData]]:
        if not madison_out:
            return {}
        madison_dict: dict[str, list[MadisonData]] = {}
        reader = csv.reader(StringIO(madison_out), delimiter="|")
        for row in reader:
            if len(row) == 3:
                pkg, ver, tail = (x.strip() for x in row[:3])
                if pkg not in madison_dict:
                    madison_dict[pkg] = []
                madison_dict[pkg].append(MadisonData(ver, tail))
            else:
                raise ValueError(f"{madison_out}\nis invalid")
        return madison_dict
