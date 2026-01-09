import struct
import uuid
from datetime import datetime, timezone
from typing import Optional


def chunk(data : list[int], n: int):
    """
    Split a sequence ints into evenly sized chunks.

    Parameters
    ----------
    data : list[int]
        The data sequence to split.
    n : int
        Size of each chunk.

    Returns
    -------
    list
        A list of sub-sequences, each of length `n` (the final one may be smaller).
    """
    return [data[i:i + n] for i in range(0, len(data), n)]


def pack(data: list[int], bit_depth: int) -> Optional[bytes]:
    """
    Pack PCM integer samples into little-endian bytes without padding.

    Parameters
    ----------
    data : list[int]
        The PCM samples to pack.
    bit_depth : int
        Bit depth of each sample (supported: 16 or 24).

    Returns
    -------
    bytes or None
        The packed bytes, or None if the bit depth is unsupported.
    """
    if bit_depth == 16:
        return struct.pack("<" + "h" * len(data), *data)
    if bit_depth == 24:
        out = bytearray()
        for x in data:
            out += x.to_bytes(3, "little", signed=True)
        return bytes(out)
    return None


def session_id() -> bytes:
    """
    Generate a 128-bit UUID for the current session.

    The UUID is returned in little-endian byte order to match the
    RACS frame header specification.

    Returns
    -------
    bytes
        16-byte little-endian representation of a UUID.
    """
    return uuid.uuid4().bytes_le

