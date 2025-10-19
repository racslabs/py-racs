import queue
import threading
import socket
from typing import Optional


class ConnectionPool:

    def __init__(self, host: str, port: int, size: int):
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

    def put(self, sock: socket.socket):
        self._pool.put(sock)

    def close(self):
        while not self._pool.empty():
            sock = self._pool.get()
            sock.close()


def recv(sock: socket.socket, n: int):
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed before full header received")
        buf.extend(chunk)
    return bytes(buf)


def send(sock: socket.socket, request: bytes) -> Optional[bytes]:
    try:
        length = len(request)
        request = length.to_bytes(8, "little") + request
        sock.sendall(request)

        header = recv(sock, 8)
        length = int.from_bytes(header, "little")

        response = recv(sock, length)
        return response

    except socket.timeout:
        print("Timed out waiting for data")
        return None
