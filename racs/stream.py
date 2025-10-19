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

    def stream(self, info: dict, pcm_data: list[int]) -> None:
        """
        Send raw PCM samples as RACS frames.

        Parameters
        ----------
        info : dict
            Dictionary containing stream metadata:
            - 'stream_id': str, unique identifier of the stream
            - 'sample_rate': int, samples per second in Hz
            - 'bit_depth': int, bits per sample (16 or 24)
            - 'channels': int, number of audio channels
            - 'chunk_size': int, size of each PCM block in bytes (max 65535)
        pcm_data : list[int]
            Raw PCM samples interleaved by channel.

        Raises
        ------
        RacsException
            If `chunk_size` is negative or exceeds 0xffff.
        """
        frame = Frame()
        frame.stream_id = info['stream_id']
        frame.sample_rate = info['sample_rate']
        frame.bit_depth = info['bit_depth']
        frame.channels = info['channels']

        chunk_size = info['chunk_size']
        if chunk_size < 0 or chunk_size > 0xffff:
            raise RacsException("'chunk_size' must be >= 0 or <= 0xffff")

        n = chunk_size // (frame.bit_depth // 8)

        for _chunk in chunk(pcm_data, n):
            frame.data = pack(_chunk, frame.bit_depth)
            sock = self._pool.get()
            try:
                resp = send(sock, frame.pack())
                unpack(resp)
            finally:
                self._pool.put(sock)

