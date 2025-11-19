from .socket import ConnectionPool, send
from .pack import unpack


class Command:
    """
    Base class for executing commands on a RACS server.

    The `Command` class provides a simple abstraction for sending
    string-based commands over a managed connection pool and
    receiving structured responses.
    """

    def __init__(self, pool: ConnectionPool):
        """
        Initialize a command executor.

        Parameters
        ----------
        pool : ConnectionPool
            The connection pool used to manage active socket connections.
        """
        self._pool = pool

    def execute_command(self, command: str):
        """
        Execute a single command on the RACS server.

        This method acquires a socket from the pool, sends the command,
        waits for a response, and then returns the connection to the pool.

        Parameters
        ----------
        command : str
            The command string to send to the server.

        Returns
        -------
        Any
            The unpacked server response.
        """
        sock = self._pool.get()
        try:
            return unpack(send(sock, command.encode() + b'\0'))
        finally:
            self._pool.put(sock)
