import struct
import crc32c
import mmh3

from .utils import session_id


class Frame:
    """
    Represents a single RACS frame containing interleaved PCM audio data.

    The client encodes raw PCM samples (interleaved by channel) into
    binary frames for transmission. Each frame consists of a 42-byte header
    followed by a PCM data block. All multi-byte fields use **little-endian**
    byte order unless noted otherwise.

    Frame Structure
    ----------------

    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | Field      | Description                                                 | Bytes      | Offset | Byte Order|
    +============+=============================================================+============+========+===========+
    | chunk_id   | ASCII string ``"rsp"``                                      | 3          | 0      | N/A       |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | session_id | 128-bit unique session ID (UUID)                            | 16         | 3      | Little    |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | stream_id  | 64-bit hash of the stream ID                                | 8          | 19     | Little    |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | checksum   | 32-bit CRC32C checksum of the PCM block                     | 4          | 27     | Little    |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | channels   | Number of audio channels                                    | 2          | 31     | Little    |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | sample_rate| Audio sample rate (samples per second)                      | 4          | 33     | Little    |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | bit_depth  | Number of bits per audio sample                             | 2          | 37     | Little    |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | block_size | Size of the PCM block in bytes (max 65,536)                 | 2          | 39     | Little    |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | flags      | Compression flag (0 = uncompressed, 1 = compressed)         | 1          | 41     | N/A       |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    | pcm_block  | Raw PCM samples interleaved by channel                      | block_size | 42     | Little    |
    +------------+-------------------------------------------------------------+------------+--------+-----------+
    """

    def __init__(self):
        """Initialize an empty RACS frame with default values."""
        self._chunk_id: bytes = b"rsp"
        self._session_id: bytes = session_id()
        self._stream_id: int = 0
        self._checksum: int = 0
        self._channels: int = 0
        self._sample_rate: int = 0
        self._bit_depth: int = 0
        self._block_size: int = 0
        self._flags: int = 0
        self._data: bytes = b""

    @property
    def chunk_id(self):
        """bytes: ASCII identifier for the frame - i.e., ``b"rsp"``"""
        return self._chunk_id

    @property
    def session_id(self):
        """bytes: 16-byte unique session identifier (UUID)."""
        return self._session_id

    @property
    def stream_id(self):
        """int: 64-bit hash representing the stream ID."""
        return self._stream_id

    @property
    def checksum(self):
        """int: CRC32C checksum of the PCM data."""
        return self._checksum

    @property
    def sample_rate(self):
        """int: Sample rate in Hz."""
        return self._sample_rate

    @property
    def bit_depth(self):
        """int: Number of bits per sample."""
        return self._bit_depth

    @property
    def block_size(self):
        """int: Size of the PCM data block in bytes."""
        return self._block_size

    @property
    def channels(self):
        """int: Number of audio channels."""
        return self._channels

    @property
    def data(self):
        """bytes: Packed PCM block containing interleaved audio samples."""
        return self._data

    @property
    def flags(self):
        """int: Compression flag (0 = uncompressed, 1 = compressed)."""
        return self._flags

    @sample_rate.setter
    def sample_rate(self, sample_rate: int):
        self._sample_rate = sample_rate

    @stream_id.setter
    def stream_id(self, stream_id: str):
        """Set the stream ID using a 64-bit Murmur3 hash of the given string."""
        self._stream_id = mmh3.hash64(stream_id)[0]

    @bit_depth.setter
    def bit_depth(self, bit_depth: int):
        self._bit_depth = bit_depth

    @channels.setter
    def channels(self, channels: int):
        self._channels = channels

    @data.setter
    def data(self, data: bytes):
        """
        Set the PCM data block and update dependent fields.

        Automatically updates:
        - `checksum`: computed via CRC32C over `data`.
        - `block_size`: set to `len(data)`.

        Parameters
        ----------
        data : bytes
            The raw PCM block containing interleaved audio samples.
        """
        self._data = data
        self._checksum = crc32c.crc32c(self._data)
        self._block_size = len(self._data)

    def pack(self) -> bytes:
        """
        Pack the frame into its binary representation.

        Returns
        -------
        bytes
            The packed frame header followed by the PCM data block.
        """
        header = struct.pack(
            "<3s16sQIHIHHB",
            self._chunk_id,
            self._session_id,
            self._stream_id,
            self._checksum,
            self._channels,
            self._sample_rate,
            self._bit_depth,
            self._block_size,
            self._flags,
        )
        return header + self._data
