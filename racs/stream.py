from .command import Command
from .pack import unpack
from .excpetion import RacsException
from .frame import Frame
from .socket import ConnectionPool, send
from .utils import chunk, pack
import zstandard as zstd
import msgpack


DEFAULT_CHUNK_SIZE = 1024 * 32
DEFAULT_BATCH_SIZE = 50
DEFAULT_COMPRESSION_LEVEL = 3


class Stream:
    """
    Base class for sending audio data to the RACS server.

    The `Stream` class handles chunking raw PCM samples into
    frames, packing them according to the RACS frame format, and
    sending them over a connection pool.
    """

    def __init__(self, pool: ConnectionPool, stream_id: str):
        """
        Initialize a new Stream instance.

        Parameters
        ----------
        pool : ConnectionPool
            Pool used to manage socket connections to the RACS server.
        """
        self._pool = pool
        self._stream_id : str = stream_id
        self._chunk_size : int = DEFAULT_CHUNK_SIZE
        self._batch_size : int = DEFAULT_BATCH_SIZE
        self._compression : bool = True
        self._compression_level : int = DEFAULT_COMPRESSION_LEVEL

    def stream_id(self, stream_id: str):
        self._stream_id = stream_id
        return self

    def chunk_size(self, chunk_size: int):
        self._chunk_size = chunk_size
        return self

    def batch_size(self, batch_size: int):
        self._batch_size = batch_size
        return self

    def compression(self, compression: bool):
        self._compression = compression
        return self

    def compression_level(self, compression_level: int):
        self._compression_level = compression_level
        return self

    def execute(self, data: list[int]):
        self._stream(
            self._stream_id,
            self._chunk_size,
            data,
            self._batch_size,
            self._compression,
            self._compression_level
        )

    def _stream(self, stream_id: str, chunk_size: int, pcm_data: list[int], batch_size: int, compression: bool, compression_level: int):
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
        batch_size : int
          Number of frames to send in each batch.
        compression : bool
          Compression flag.
        compression_level : int
          Level of compression.

        Raises
        ------
        RacsException
          If `chunk_size` is negative or exceeds 0xffff.
        """
        command = Command(self._pool)
        bit_depth = command.execute_command(f"META '{stream_id}' 'bit_depth'")

        command.execute_command(f"OPEN '{stream_id}'")

        if chunk_size < 0 or chunk_size > 0xffff:
            raise RacsException("'chunk_size' must be >= 0 or <= 0xffff")

        frame = Frame()
        frame.stream_id = stream_id
        frame.flags = compression

        cctx = zstd.ZstdCompressor(level=compression_level)

        n = chunk_size // (bit_depth // 8)
        frames = []

        def flush():
            nonlocal frames
            if len(frames) == 0:
                return

            sock = self._pool.get()
            try:
                buf = bytearray(b"rsp")
                buf.extend(msgpack.packb(frames, use_bin_type=True))

                resp = send(sock, bytes(buf))
                unpack(resp)
            finally:
                self._pool.put(sock)

            frames.clear()

        for chunk_ in chunk(pcm_data, n):
            data = pack(chunk_, bit_depth)

            if compression:
                frame.data = cctx.compress(data)
            else:
                frame.data = data

            frames.append(frame.pack())

            if len(frames) == batch_size:
                flush()

        flush()
        command.execute_command(f"CLOSE '{stream_id}'")
