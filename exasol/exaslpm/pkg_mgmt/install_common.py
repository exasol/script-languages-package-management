from dataclasses import dataclass

@dataclass
class CommandExecInfo:
    cmd: list[str]
    err: str

def check_error(ret_val, msg, log):
    if ret_val != 0:
        log(msg)
        return False
    return True