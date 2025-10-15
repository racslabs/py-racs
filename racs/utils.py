import struct
import time
from datetime import datetime, timezone
from typing import Optional

import mmh3


def chunk(data, n):
    return [data[i:i + n] for i in range(0, len(data), n)]


def pack(data: list[int], bit_depth) -> Optional[bytes]:
    if bit_depth == 16:
        return struct.pack("<" + "h" * len(data), *data)
    if bit_depth == 24:
        out = bytearray()
        for x in data:
            out += x.to_bytes(3, "little", signed=True)
        return bytes(out)
    return None


def session_id() -> tuple[int, int]:
    seed = str(int(time.time()))
    return mmh3.hash64(seed, signed=False)


def rfc3339(dt: datetime) -> str:
    return dt.astimezone(timezone.utc)\
        .isoformat(timespec='milliseconds')\
        .replace('+00:00', 'Z')
