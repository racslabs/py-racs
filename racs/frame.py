import struct
import crc32c
import mmh3

from .utils import session_id


class Frame:
    def __init__(self):
        self._chunk_id: bytes = b"rsp"
        self._session_id: tuple[int, int] = session_id()
        self._stream_id: int = 0
        self._checksum: int = 0
        self._channels: int = 0
        self._sample_rate: int = 0
        self._bit_depth: int = 0
        self._block_size: int = 0
        self._data: bytes = b""

    @property
    def chunk_id(self):
        return self._chunk_id

    @property
    def session_id(self):
        return self._session_id

    @property
    def stream_id(self):
        return self._stream_id

    @property
    def checksum(self):
        return self._checksum

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def bit_depth(self):
        return self._bit_depth

    @property
    def block_size(self):
        return self._block_size

    @property
    def channels(self):
        return self._channels

    @property
    def data(self):
        return self._data

    @sample_rate.setter
    def sample_rate(self, sample_rate: int):
        self._sample_rate = sample_rate

    @stream_id.setter
    def stream_id(self, stream_id: str):
        self._stream_id = mmh3.hash64(stream_id)[0]

    @bit_depth.setter
    def bit_depth(self, bit_depth: int):
        self._bit_depth = bit_depth

    @channels.setter
    def channels(self, channels: int):
        self._channels = channels

    @data.setter
    def data(self, data: bytes):
        self._data = data
        self._checksum = crc32c.crc32c(self._data)
        self._block_size = len(self._data)

    def encode(self) -> bytes:
        header = struct.pack(
            "<3sQQQ I H I H H",
            self._chunk_id,
            self._session_id[0],
            self._session_id[1],
            self._stream_id,
            self._checksum,
            self._channels,
            self._sample_rate,
            self._bit_depth,
            self._block_size
        )
        return header + self._data
