import threading
import time
from collections import deque
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)

from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandResult
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import CommandLogger


class StreamSplitter:
    def __init__(self, source_stream):
        self.source = source_stream
        self.stdout_deque = deque()
        self.stderr_deque = deque()
        self.condition = threading.Condition()
        self.finished = False

        # Start the consumer thread
        self.thread = threading.Thread(target=self._consume, daemon=True)
        self.thread.start()

    def _consume(self):
        try:
            for stdout_chunk, stderr_chunk in self.source:
                with self.condition:
                    if stdout_chunk:
                        self.stdout_deque.append(stdout_chunk.decode("utf-8"))
                    if stderr_chunk:
                        self.stderr_deque.append(stderr_chunk.decode("utf-8"))
                    self.condition.notify_all()
        finally:
            with self.condition:
                self.finished = True
                self.condition.notify_all()

    def _get_iterator(self, target_deque):
        while True:
            with self.condition:
                while not target_deque and not self.finished:
                    self.condition.wait()

                if target_deque:
                    yield target_deque.popleft()
                elif self.finished:
                    break

    @property
    def stdout_iter(self):
        return self._get_iterator(self.stdout_deque)

    @property
    def stderr_iter(self):
        return self._get_iterator(self.stderr_deque)


class DockerCommandExecutor:
    def __init__(self, logger: CommandLogger, test_container: DockerTestContainer):
        self._log = logger
        self._test_container = test_container

    def execute(self, cmd_strs: list[str], env_variables: dict[str, str] | None =None) -> CommandResult:
        docker_client = self._test_container.container.client
        exec_instance = docker_client.api.exec_create(
            self._test_container.container.id,
            cmd_strs,
            environment=env_variables,
            tty=False,
        )

        exec_output = docker_client.api.exec_start(
            exec_instance["Id"],
            tty=False,
            stream=True,
            demux=True,
        )

        stream_splitter = StreamSplitter(exec_output)

        def return_code():
            stream_splitter.thread.join()
            if not stream_splitter.finished:
                raise RuntimeError("Stream not finished")
            for i in range(100):
                exit_metadata = docker_client.api.exec_inspect(exec_instance["Id"])
                if not exit_metadata["Running"]:
                    return exit_metadata["ExitCode"]
                time.sleep(1)
            raise RuntimeError("Command did not exit cleanly.")

        return CommandResult(
            fn_ret_code=return_code,
            stdout=stream_splitter.stdout_iter,
            stderr=stream_splitter.stderr_iter,
            logger=self._log,
        )
