from .excpetion import RacsException
from .socket import SocketPool, send
from .pack import unpack
from .frame import Frame
from .utils import chunk, pack


class Command:
    def __init__(self, pool: SocketPool):
        self._pool = pool

    def execute_command(self, command: str):
        sock = self._pool.get()
        try:
            return unpack(send(sock, command.encode() + b'\0'))
        finally:
            self._pool.put(sock)

    def stream(self, info, pcm_data: list[int]) -> None:
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
                resp = send(sock, frame.encode())
                unpack(resp)
            finally:
                self._pool.put(sock)
