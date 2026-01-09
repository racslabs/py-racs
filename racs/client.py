from .pipeline import Pipeline
from .socket import ConnectionPool
from .command import Command
from .stream import Stream


class Racs(Command):
    """
    High-level client interface for interacting with the RACS server.

    The `Racs` class manages a pool of socket connections and provides
    a simple interface for sending commands and executing pipelines.
    """
    def __init__(self, host: str, port: int, pool_size: int = 3):
        """
        Initialize a new RACS client instance.

        Parameters
        ----------
        host : str
            The hostname or IP address of the RACS server.
        port : int
            The port number to connect to.
        pool_size : int, optional
            The number of socket connections to maintain in the pool (defaults to 3).
        """
        super().__init__(ConnectionPool(host, port, pool_size))

    def pipeline(self):
        """
        Create a new pipeline for chained command execution.

        Returns
        -------
        Pipeline
            A :class:`Pipeline` instance allows composing multiple RACS server
            commands into a single executable sequence. Commands are joined using
            the pipe operator (`|>`) and executed sequentially.
        """
        return Pipeline(self._pool)

    def stream(self, stream_id):
        return Stream(self._pool, stream_id)
