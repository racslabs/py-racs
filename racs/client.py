from .pipeline import Pipeline
from .socket import SocketPool
from .command import Command


class Racs(Command):
    def __init__(self, host: str, port: int, pool_size: int = 3):
        super().__init__(SocketPool(host, port, pool_size))

    def pipeline(self):
        return Pipeline(self._pool)
