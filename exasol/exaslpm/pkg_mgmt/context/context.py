from dataclasses import dataclass

from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandExecutor
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import CommandLogger
from exasol.exaslpm.pkg_mgmt.context.file_access import FileAccess
from exasol.exaslpm.pkg_mgmt.context.file_downloader import FileDownloader
from exasol.exaslpm.pkg_mgmt.context.history_file_manager import HistoryFileManager
from exasol.exaslpm.pkg_mgmt.context.temp_file_provider import TempFileProvider


@dataclass(frozen=True)
class Context:
    cmd_logger: CommandLogger
    cmd_executor: CommandExecutor
    history_file_manager: HistoryFileManager
    file_access: FileAccess
    file_downloader: FileDownloader
    temp_file_provider: TempFileProvider
