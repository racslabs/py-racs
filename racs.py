import socket
import queue
import threading
import msgpack
import struct
import mmh3
import crc32c

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
    return data[1:]

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
        self._chunk_id: bytes = b"rspt"
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
    def pack(data :list[int]) -> bytes:
        b = b""
        for i in data:
            b += i.to_bytes(2, "little", signed=True)
        return b

class Command:
    def __init__(self, pool: SocketPool):
        self._pool = pool

    def execute(self, command: str):
        sock = self._pool.get()
        try:
            return decode(send_request(sock, command.encode()))
        finally:
            self._pool.put(sock)

    def stream(self, info, pcm_data: list[int]) -> None:
        for chunk in Frame.chunk(pcm_data, info['chunk_size']):
            frame = Frame()
            frame.stream_id = info['stream_id']
            frame.sample_rate = info['sample_rate']
            frame.bit_depth = 16
            frame.channels = info['channels']
            frame.data = Frame.pack(chunk)

            sock = self._pool.get()
            try:
                resp = send_request(sock, frame.encode())
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

    def commit(self):
        return self.execute(" |> ".join(self._commands))

    def reset(self):
        self._commands.clear()


def rfc3339(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

class RacsException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Racs(Command):
    def __init__(self, host: str, port: int, pool_size: int = 10):
        super().__init__(SocketPool(host, port, pool_size))

    def pipeline(self):
        return Pipeline(self._pool)


if __name__ == '__main__':
    # import torchaudio
    #
    # waveform, sample_rate = torchaudio.load("47178__suspiciononline__saxu.mp3")  # waveform: (channels, samples), float32 in [-1.0, 1.0]
    # data = (waveform * 32768).clamp(min=-32768, max=32767).short().reshape(waveform.shape[1]).tolist()

    r = Racs("localhost", 8080)
    pipe = r.pipeline()
    # pipe.create('poo', 44100, 1)
    # pipe.commit()
    # pipe.reset()
    #
    # pipe.open('poo')
    # pipe.commit()
    # pipe.reset()

    # pipe.stream({
    #     'chunk_size': 1024,
    #     'sample_rate': 44100,
    #     'stream_id': 'poo',
    #     'channels': 1
    # }, data)

    frm = datetime(2023, 12, 25, 17, 30, 45, 123000)
    to = datetime(2026, 5, 26, 22, 56, 16, 123000)

    d = pipe.extract('poo', frm, to).format('audio/mpeg', 1, 44100).commit()

    with open("yo.mp3", "wb") as f:
        f.write(d)
