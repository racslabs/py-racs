import socket
import queue
import threading
import msgpack
import struct

from datetime import datetime, timezone
from uuid import getnode as get_mac

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
        s.settimeout(0.1)
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


def send_request(sock :socket.socket, request: bytes) -> bytes | None:
    response = b''

    try:
        sock.sendall(request)
        response += sock.recv(1024)

        while True:
            response += sock.recv(1024)
    except socket.timeout:
        pass

    finally:
        pass

    return response


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

def decode_list(data) -> []:
    return data[1]

def decode_u8v(data) -> bytes:
    return data[1]

def decode_i16v(data) -> [int]:
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
        self._chunk_id: bytes = b"atsp"
        self._mac_addr: int = get_mac()
        self._stream_id: int = 0
        self._checksum: int = 0
        self._channels: int = 0
        self._sample_rate: int = 0
        self._bit_depth: int = 0
        self._block_size: int = 0
        self._data :bytes = b""

    @property
    def chunk_id(self):
        return self._chunk_id

    @property
    def mac_addr(self):
        return self._mac_addr

    @property
    def stream_id(self):
        return self._stream_id

    @stream_id.setter
    def stream_id(self, stream_id):
        self._stream_id = stream_id

    @property
    def checksum(self):
        return self._checksum

    @checksum.setter
    def checksum(self, checksum):
        self._checksum = checksum

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sample_rate):
        self._sample_rate = sample_rate

    @property
    def bit_depth(self):
        return self._bit_depth

    @bit_depth.setter
    def bit_depth(self, bit_depth):
        self._bit_depth = bit_depth

    @property
    def block_size(self):
        return self._block_size

    @block_size.setter
    def block_size(self, block_size):
        self._block_size = block_size

    @property
    def channels(self):
        return self._channels

    @channels.setter
    def channels(self, channels):
        self._channels = channels

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def encode(self):
        b = b""
        b += self._chunk_id
        b += self._mac_addr.to_bytes(6, "little")
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
    def pack(data :[int]) -> bytes:
        b = b""
        for i in data:
            b += i.to_bytes(2, "little", signed=True)
        return b

class CommandBase:
    def __init__(self, pool: SocketPool):
        self._pool = pool

    def exec(self, command: str):
        sock = self._pool.get()
        try:
            return decode(send_request(sock, command.encode()))
        finally:
            self._pool.put(sock)

    def stream(self, stream_id: str, sample_rate: int, channels: int, pcm_data: list[int]) -> None:
        for chunk in Frame.chunk(pcm_data, 1024):
            frame = Frame()
            frame.stream_id = stream_id
            frame.sample_rate = sample_rate
            frame.bit_depth = 16
            frame.channels = channels
            frame.data = Frame.pack(chunk)
            frame.block_size = len(frame.data)

            sock = self._pool.get()
            try:
                send_request(sock, frame.encode())
            finally:
                self._pool.put(sock)

    def extract(self, stream_id: str, start: datetime, end: datetime):
        print(f"EXTRACT '{stream_id}' {utc_iso8601(start)} {utc_iso8601(end)} ")
        return self.exec(f"EXTRACT '{stream_id}' {utc_iso8601(start)} {utc_iso8601(end)} ")

    def create(self, stream_id: str, sample_rate: int, channels: int):
        return self.exec(f"STREAMCREATE '{stream_id}' {sample_rate} {channels} ")

    def info(self, stream_id: str, attr: str):
        return self.exec(f"STREAMINFO '{stream_id}' '{attr}' ")

    def list(self, glob: str):
        return self.exec(f"STREAMLIST '{glob}' ")

    def open(self, stream_id: str):
        return self.exec(f"STREAMOPEN '{stream_id}' ")

    def close(self, stream_id: str):
        return self.exec(f"STREAMCLOSE '{stream_id}' ")

    def eval(self, expr: str):
        return self.exec(f"EVAL '{expr}' ")

    def ping(self):
        return self.exec("PING ")


def utc_iso8601(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

class RacsException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Command(CommandBase):
    def __init__(self, pool: SocketPool):
        super().__init__(pool)

class Racs(Command):
    def __init__(self, host: str, port: int):
        super().__init__(SocketPool(host, port, 5))


if __name__ == '__main__':
    racs = Racs("localhost", 8080)
    print(racs.exec("EXTRACT 'poo' 2023-12-25T22:30:45.123Z 2026-12-25T22:30:45.123Z"))

    # frm = datetime(2023, 12, 25, 17, 30, 45, 123000)
    # to = datetime(2026, 12, 25, 17, 30, 45, 123000)
    # print(racs.extract("poo", frm, to))