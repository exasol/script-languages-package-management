from collections.abc import Callable
from dataclasses import dataclass

from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.context.context import Context


@dataclass
class CommandExecInfo:
    cmd: list[str]
    err: str
    env: dict[str, str] | None = None


def check_error(ret_val: int, msg: str, log: Callable[[str], None]) -> bool:
    if ret_val != 0:
        log(msg)
        return False
    return True


def run_cmd(cmd: CommandExecInfo, ctx: Context):
    cmd_res = ctx.cmd_executor.execute(cmd.cmd, cmd.env)
    cmd_res.print_results()
    if not check_error(cmd_res.return_code(), cmd.err, ctx.cmd_logger.err):
        raise CommandFailedException(cmd.err)
