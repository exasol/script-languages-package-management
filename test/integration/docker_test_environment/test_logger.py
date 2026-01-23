class TestLogger:
    def __init__(self) -> None:
        self.info_messages = ""
        self.warning_messages = ""
        self.error_messages = ""

    def info(self, msg: str, **kwargs) -> None:
        self.info_messages += msg + str(kwargs)

    def warn(self, msg: str, **kwargs) -> None:
        self.warning_messages += msg + str(kwargs)

    def err(self, msg: str, **kwargs) -> None:
        self.error_messages += msg + str(kwargs)
