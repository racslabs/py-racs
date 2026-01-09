from .socket import ConnectionPool
from .command import Command

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

    def gain(self, gain: float):
        """
        Append a GAIN command to the pipeline.

        Command String Example
        ----------------------
        GAIN 0.75

        Parameters
        ----------
        gain : float
            Linear gain multiplier to apply to the signal.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"GAIN {float(gain)}")
        return self

    def trim(self, left: float, right: float):
        """
        Append a TRIM command to the pipeline.

        Command String Example
        ----------------------
        TRIM 1.5 10.0

        Parameters
        ----------
        left : float
            Start time in seconds to trim from.
        right : float
            End time in seconds to trim to.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"TRIM {float(left)} {float(right)}")
        return self

    def fade(self, in_sec: float, out_sec: float):
        """
        Append a FADE command to the pipeline.

        Command String Example
        ----------------------
        FADE 0.5 1.0

        Parameters
        ----------
        in_sec : float
            Fade-in duration in seconds.
        out_sec : float
            Fade-out duration in seconds.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"FADE {float(in_sec)} {float(out_sec)}")
        return self

    def pan(self, pan: float):
        """
        Append a PAN command to the pipeline.

        Command String Example
        ----------------------
        PAN -0.25

        Parameters
        ----------
        pan : float
            Stereo pan position. Typically in the range [-1.0, 1.0],
            where -1 is full left and 1 is full right.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"PAN {float(pan)}")
        return self

    def pad(self, left: float, right: float):
        """
        Append a PAD command to the pipeline.

        Command String Example
        ----------------------
        PAD 1.0 2.5

        Parameters
        ----------
        left : float
            Amount of silence (in seconds) to pad at the beginning.
        right : float
            Amount of silence (in seconds) to pad at the end.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"PAD {float(left)} {float(right)}")
        return self

    def clip(self, min_val: int, max_val: int):
        """
        Append a CLIP command to the pipeline.

        Command String Example
        ----------------------
        CLIP -32768 32767

        Parameters
        ----------
        min_val : int
            Minimum sample value.
        max_val : int
            Maximum sample value.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"CLIP {min_val} {max_val}")
        return self

    def split(self, channel: int):
        """
        Append a SPLIT command to the pipeline.

        Command String Example
        ----------------------
        SPLIT 0

        Parameters
        ----------
        channel : str
            Channel number to extract.
        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"SPLIT {channel}")
        return self

    def range(self, stream_id: str, start: float, duration: float):
        """
        Append an RANGE command to the pipeline.

        Command String Example
        ----------------------
        RANGE 'vocals' 0.0 30.0

        Parameters
        ----------
        stream_id : str
            Identifier of the target stream. ASCII only.
        start : float
            Start time (in seconds) to extract from stream.
        duration : float
            Duration of audio segment to extract from stream.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"RANGE '{stream_id}' {float(start)} {float(duration)}")
        return self

    def encode(self, mime_type: str):
        """
        Append a ENCODE command to the pipeline.

        Command String Example
        ----------------------
        ENCODE 'audio/wav'

        Parameters
        ----------
        mime_type : str
            MIME type of the output (e.g., "audio/wav").

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"ENCODE '{mime_type}'")
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

    def meta(self, stream_id: str, attr: str):
        """
        Append an META command to the pipeline.

        Command String Example
        ----------------------
        META 'vocals' 'size'

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
        self._commands.append(f"META '{stream_id}' '{attr}'")
        return self

    def list(self, pattern: str):
        """
        Append an LIST command to the pipeline.

        Command String Example
        ----------------------
        LIST 'vocals*'

        Parameters
        ----------
        pattern : str
            Glob-style pattern for stream names.

        Returns
        -------
        Pipeline
            The current pipeline instance (for chaining).
        """
        self._commands.append(f"LIST '{pattern}'")
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
        RANGE 'vocals' 0.0 30.0 |> ENCODE 'audio/wav'

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

        After calling reset(), `_commands` is empty and no command will
        be sent until new commands are appended.
        """
        self._commands.clear()
