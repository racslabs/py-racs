from datetime import datetime

from .socket import SocketPool
from .command import Command
from .utils import rfc3339


class Pipeline(Command):
    def __init__(self, pool: SocketPool):
        super().__init__(pool)
        self._commands = []

    def extract(self, stream_id: str, frm: datetime, to: datetime):
        self._commands.append(f"EXTRACT '{stream_id}' {rfc3339(frm)} {rfc3339(to)}")
        return self

    def format(self, mime_type: str, sample_rate: int, channels: int, bit_depth: int):
        self._commands.append(f"FORMAT '{mime_type}' {sample_rate} {channels} {bit_depth}")
        return self

    def create(self, stream_id: str, sample_rate: int, channels: int, bit_depth: int):
        self._commands.append(f"CREATE '{stream_id}' {sample_rate} {channels} {bit_depth}")
        return self

    def info(self, stream_id: str, attr: str):
        self._commands.append(f"INFO '{stream_id}' '{attr}'")
        return self

    def list(self, pattern: str):
        self._commands.append(f"LS '{pattern}'")
        return self

    def open(self, stream_id: str):
        self._commands.append(f"OPEN '{stream_id}'")
        return self

    def close(self, stream_id: str):
        self._commands.append(f"CLOSE '{stream_id}'")
        return self

    def eval(self, expr: str):
        self._commands.append(f"EVAL '{expr}'")
        return self

    def ping(self):
        self._commands.append("PING")
        return self

    def shutdown(self):
        self._commands.append("SHUTDOWN")
        return self

    def execute(self):
        command = " |> ".join(self._commands)
        print(command)
        return self.execute_command(command)

    def reset(self):
        self._commands.clear()
