from datetime import datetime

from .socket import ConnectionPool
from .command import Command
from .utils import rfc3339

class Pipeline(Command):
    """
    Represents a chainable RACS command pipeline.

    The `Pipeline` class allows composing multiple RACS server commands
    into a single executable sequence. Commands are joined using the
    pipe operator (`|>`) and executed as one compound command.
    """

    def __init__(self, pool: ConnectionPool):
        """
        Initialize a new pipeline.

        Parameters
        ----------
        pool : ConnectionPool
            Connection pool managing socket connections to the RACS server.
        """
        super().__init__(pool)
        self._commands = []

    def extract(self, stream_id: str, frm: datetime, to: datetime):
        """
        Append an EXTRACT command to the pipeline.

        Command String Example
        ----------------------
        EXTRACT 'vocals' 2025-10-18T12:00:00Z 2025-10-18T12:05:00Z

        Parameters
        ----------
        stream_id : str
            Identifier of the target stream. ASCII only.
        frm : datetime
            Start time in RFC 3339 format.
        to : datetime
            End time in RFC 3339 format.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"EXTRACT '{stream_id}' {rfc3339(frm)} {rfc3339(to)}")
        return self

    def format(self, mime_type: str, sample_rate: int, channels: int, bit_depth: int):
        """
        Append a FORMAT command to the pipeline.

        Command String Example
        ----------------------
        FORMAT 'audio/wav' 48000 2 16

        Parameters
        ----------
        mime_type : str
            MIME type of the output (e.g., "audio/wav").
        sample_rate : int
            Sample rate in Hz.
        channels : int
            Number of audio channels.
        bit_depth : int
            Bits per sample.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"FORMAT '{mime_type}' {sample_rate} {channels} {bit_depth}")
        return self

    def create(self, stream_id: str, sample_rate: int, channels: int, bit_depth: int):
        """
        Append a CREATE command to the pipeline.

        Command String Example
        ----------------------
        CREATE 'vocals' 48000 2 16

        Parameters
        ----------
        stream_id : str
            Unique identifier for the new stream. ASCII only.
        sample_rate : int
            Sample rate in Hz.
        channels : int
            Number of audio channels.
        bit_depth : int
            Bits per sample.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"CREATE '{stream_id}' {sample_rate} {channels} {bit_depth}")
        return self

    def info(self, stream_id: str, attr: str):
        """
        Append an INFO command to the pipeline.

        Command String Example
        ----------------------
        INFO 'vocals' 'size'

        Parameters
        ----------
        stream_id : str
            Identifier of the target stream. ASCII only.
        attr : str
            Metadata field to retrieve.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"INFO '{stream_id}' '{attr}'")
        return self

    def list(self, pattern: str):
        """
        Append an LS command to the pipeline.

        Command String Example
        ----------------------
        LS 'vocals*'

        Parameters
        ----------
        pattern : str
            Glob-style pattern for stream names.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"LS '{pattern}'")
        return self

    def open(self, stream_id: str):
        """
        Append an OPEN command to the pipeline.

        Command String Example
        ----------------------
        OPEN 'vocals'

        Parameters
        ----------
        stream_id : str
            Identifier of the stream to open. ASCII only.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"OPEN '{stream_id}'")
        return self

    def close(self, stream_id: str):
        """
        Append a CLOSE command to the pipeline.

        Command String Example
        ----------------------
        CLOSE 'vocals'

        Parameters
        ----------
        stream_id : str
            Identifier of the stream to close. ASCII only.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"CLOSE '{stream_id}'")
        return self

    def eval(self, expr: str):
        """
        Append an EVAL command to the pipeline.

        Command String Example
        ----------------------
        EVAL '(+ 1 2 3)'

        Parameters
        ----------
        expr : str
            Scheme expression to evaluate.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"EVAL '{expr}'")
        return self

    def ping(self):
        """
        Append a PING command to the pipeline.

        Command String Example
        ----------------------
        PING

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append("PING")
        return self

    def shutdown(self):
        """
        Append a SHUTDOWN command to the pipeline.

        Command String Example
        ----------------------
        SHUTDOWN

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append("SHUTDOWN")
        return self

    def execute(self):
        """
        Execute all appended commands as a single pipeline.

        Command String Example
        ----------------------
        EXTRACT 'vocals' 2025-10-18T12:00:00Z 2025-10-18T12:05:00Z |> FORMAT 'audio/wav' 48000 2 16

        Returns
        -------
        Any
            The unpacked response from the RACS server.
        """
        command = " |> ".join(self._commands)
        return self.execute_command(command)

    def reset(self):
        """
        Clear all commands in the pipeline.

        Command String Example
        ----------------------
        After calling reset(), `_commands` is empty and no command will
        be sent until new commands are appended.
        """
        self._commands.clear()
