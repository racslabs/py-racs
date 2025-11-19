from .command import Command
from .pack import unpack
from .excpetion import RacsException
from .frame import Frame
from .socket import ConnectionPool, send
from .utils import chunk, pack


class Stream:
    """
    Base class for sending audio data to the RACS server.

    The `Stream` class handles chunking raw PCM samples into
    frames, packing them according to the RACS frame format, and
    sending them over a connection pool.
    """

    def __init__(self, pool: ConnectionPool):
        """
        Initialize a new Stream instance.

        Parameters
        ----------
        pool : ConnectionPool
            Pool used to manage socket connections to the RACS server.
        """
        self._pool = pool

    def stream(self, stream_id: str, chunk_size: int, pcm_data: list[int]) -> None:
        """
        Send raw PCM samples as RACS frames.

        Parameters
        ----------
        stream_id : str
            Unique identifier of the stream. ASCII string.
        chunk_size :
            Size of pcm block in bytes. Must be >= 0 or <= 0xffff.
        pcm_data : list[int]
            Raw PCM samples interleaved by channel.

        Raises
        ------
        RacsException
            If `chunk_size` is negative or exceeds 0xffff.
        """
        command = Command(self._pool)
        bit_depth = command.execute_command(f"INFO '{stream_id}' 'bit_depth'")

        frame = Frame()
        frame.stream_id = stream_id

        if chunk_size < 0 or chunk_size > 0xffff:
            raise RacsException("'chunk_size' must be >= 0 or <= 0xffff")

        n = chunk_size // (bit_depth // 8)

        for _chunk in chunk(pcm_data, n):
            frame.data = pack(_chunk, bit_depth)
            sock = self._pool.get()
            try:
                resp = send(sock, frame.pack())
                unpack(resp)
            finally:
                self._pool.put(sock)

