import random
import socket
import queue
import threading
import time
from typing import Any

import msgpack
import struct
import mmh3
import crc32c

from datetime import datetime, timezone

class SocketPool:

    def __init__(self, host :str, port :int, size :int):
        self._host = host
        self._port = port
        self._size = size
        self._pool = queue.Queue()
        self._lock = threading.Lock()

        for _ in range(self._size):
            self._pool.put(self.create_socket())

    def create_socket(self) -> socket.socket:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(None)
        s.connect((self._host, self._port))
        return s

    def get(self):
        return self._pool.get()

    def put(self, sock :socket.socket):
        self._pool.put(sock)

    def close(self):
        while not self._pool.empty():
            sock = self._pool.get()
            sock.close()


def send(sock: socket.socket, request: bytes) -> bytes | None:
    try:
        length = len(request)
        request = length.to_bytes(8, "little") + request
        sock.sendall(request)

        data = sock.recv(8)
        if not data:
            return None
        length = int.from_bytes(data, "little")

        response = bytearray()
        while len(response) < length:
            chunk = sock.recv(min(4096, length - len(response)))
            if not chunk:
                raise ConnectionError("Socket closed before full message received")
            response.extend(chunk)

        return bytes(response)

    except socket.timeout:
        print("Timed out waiting for data")
        return None


def decode_error(data):
    raise RacsException(data[1])

def decode_bool(data) -> bool:
    return data[1]

def decode_int(data) -> int:
    return data[1]

def decode_float(data) -> float:
    return data[1]

def decode_str(data) -> str:
    return data[1]

def decode_null(data) -> None:
    return None

def decode_list(data) -> list[Any]:
    return data[1:]

def decode_u8v(data) -> bytes:
    return data[1]

def decode_i16v(data) -> list[Any]:
    return [x[0] for x in struct.iter_unpack('<h', data[1])]

def decode(b):
    data = msgpack.unpackb(b)

    tp = data[0]
    if tp == "string":
        return decode_str(data)
    if tp == "error":
        return decode_error(data)
    if tp == "int":
        return decode_int(data)
    if tp == "float":
        return decode_float(data)
    if tp == "null":
        return decode_null(data)
    if tp == "list":
        return decode_list(data)
    if tp == "u8v" or tp == "i8v":
        return decode_u8v(data)
    if tp == "i16v":
        return decode_i16v(data)

    return None

class Frame:
    def __init__(self):
        self._chunk_id: bytes = b"rspt"
        self._session_id: tuple[int, int] = create_session_id()
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

    @stream_id.setter
    def stream_id(self, stream_id: str):
        self._stream_id = mmh3.hash64(stream_id)[0]

    @property
    def checksum(self):
        return self._checksum

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sample_rate: int):
        self._sample_rate = sample_rate

    @property
    def bit_depth(self):
        return self._bit_depth

    @bit_depth.setter
    def bit_depth(self, bit_depth: int):
        self._bit_depth = bit_depth

    @property
    def block_size(self):
        return self._block_size

    @property
    def channels(self):
        return self._channels

    @channels.setter
    def channels(self, channels: int):
        self._channels = channels

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: list[int]):
        self._data = data
        self._checksum = crc32c.crc32c(self._data)
        self._block_size = len(self._data)

    def encode(self):
        b = b""
        b += self._chunk_id
        b += self._session_id[0].to_bytes(8, "little")
        b += self._session_id[1].to_bytes(8, "little")
        b += self._stream_id.to_bytes(8, "little")
        b += self._checksum.to_bytes(4, "little")
        b += self._channels.to_bytes(2, "little")
        b += self._sample_rate.to_bytes(4, "little")
        b += self._bit_depth.to_bytes(2, "little")
        b += self._block_size.to_bytes(2, "little")
        b += self._data

        return b

    @staticmethod
    def chunk(data, n):
        return [data[i:i + n] for i in range(0, len(data), n)]

    @staticmethod
    def pack(data :list[int]) -> bytes:
        b = b""
        for i in data:
            b += i.to_bytes(2, "little", signed=True)
        return b


def create_session_id() -> tuple[int, int]:
    timestamp = str(int(time.time()))
    return mmh3.hash64(timestamp, signed=False)

class Command:
    def __init__(self, pool: SocketPool):
        self._pool = pool

    def execute(self, command: str):
        sock = self._pool.get()
        try:
            return decode(send(sock, command.encode() + b'\0'))
        finally:
            self._pool.put(sock)

    def stream(self, info, pcm_data: list[int]) -> None:
        frame = Frame()
        frame.stream_id = info['stream_id']
        frame.sample_rate = info['sample_rate']
        frame.bit_depth = 16
        frame.channels = info['channels']

        for chunk in Frame.chunk(pcm_data, info['chunk_size']):
            frame.data = Frame.pack(chunk)
            sock = self._pool.get()
            try:
                resp = send(sock, frame.encode())
                decode(resp)
            finally:
                self._pool.put(sock)


class Pipeline(Command):
    def __init__(self, pool: SocketPool):
        super().__init__(pool)
        self._commands = []

    def extract(self, stream_id: str, frm: datetime, to: datetime):
        self._commands.append(f"EXTRACT '{stream_id}' {rfc3339(frm)} {rfc3339(to)}")
        return self

    def format(self, mime_type: str, channels: int, sample_rate: int):
        self._commands.append(f"FORMAT '{mime_type}' {channels} {sample_rate}")
        return self

    def create(self, stream_id: str, sample_rate: int, channels: int):
        self._commands.append(f"CREATE '{stream_id}' {sample_rate} {channels}")
        return self

    def info(self, stream_id: str, attr: str):
        self._commands.append(f"INFO '{stream_id}' '{attr}'")
        return self

    def list(self, pattern: str):
        self._commands.append(f"LIST '{pattern}'")
        return self

    def open(self, stream_id: str):
        self._commands.append(f"OPEN '{stream_id}'")
        return self

    def close(self, stream_id: str):
        self._commands.append(f"CLOSE '{stream_id}'")
        return self

    def eval(self, expr: str):
        self._commands.append(f"EVAL '{expr}'")
        return self

    def ping(self):
        self._commands.append("PING")
        return self

    def shutdown(self):
        self._commands.append("SHUTDOWN")
        return self

    def execute_pipeline(self):
        command = " |> ".join(self._commands)
        print(command)
        return self.execute(command)

    def reset(self):
        self._commands.clear()


def rfc3339(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

class RacsException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Racs(Command):
    def __init__(self, host: str, port: int, pool_size: int = 3):
        super().__init__(SocketPool(host, port, pool_size))

    def pipeline(self):
        return Pipeline(self._pool)
