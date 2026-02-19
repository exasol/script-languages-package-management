import csv
import re
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
    version: str
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

        def consume_stdout(line: str | bytes, **kwargs) -> None:
            if isinstance(line, bytes):
                line = line.decode()
            stdout_lines.append(line)

        def consume_stderr(_line: str | bytes, **kwargs) -> None:
            pass

        ret_code = cmd_res.consume_results(consume_stdout, consume_stderr)
        if ret_code != 0:
            raise CommandFailedException("Failed executing madison")
        return " ".join(stdout_lines)


class MadisonParser:
    @staticmethod
    def is_match(text: str, pattern: str) -> bool:
        # 1. Escape special regex characters so they are treated as literal text
        # 2. Replace the escaped asterisk '\*' back to the regex wildcard '.*'
        regex_pattern = re.escape(pattern).replace(r"\*", ".*")

        # 3. Add anchors (^ and $) to ensure we match the ENTIRE string,
        # not just a piece of it in the middle.
        full_regex = f"^{regex_pattern}$"

        # Use re.fullmatch for a clean boolean check
        return bool(re.fullmatch(full_regex, text))

    @staticmethod
    def parse_madison_output(
        madison_out: str, ctx: Context
    ) -> dict[str, list[MadisonData]]:
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
                ctx.cmd_logger.err(f"Invalid madison output: {madison_out}")
                raise ValueError(f"{row}\nis invalid")
        return madison_dict
