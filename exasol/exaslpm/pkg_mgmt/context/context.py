from dataclasses import dataclass

from exasol.exaslpm.pkg_mgmt.context.binary_checker import BinaryChecker
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandExecutor
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import CommandLogger
from exasol.exaslpm.pkg_mgmt.context.history_file_manager import HistoryFileManager


@dataclass
class Context:
    cmd_logger: CommandLogger
    cmd_executor: CommandExecutor
    history_file_manager: HistoryFileManager
    binary_checker: BinaryChecker
