import struct
import msgpack
from typing import Any

from .excpetion import RacsException


def unpack_bool(data) -> bool:
    return data[1]


def unpack_int(data) -> int:
    return data[1]


def unpack_float(data) -> float:
    return data[1]


def unpack_str(data) -> str:
    return data[1]


def unpack_null(data) -> None:
    return None


def unpack_list(data) -> list[Any]:
    return data[1:]


def unpack_u8v(data) -> bytes:
    return data[1]


def unpack_s16v(data) -> list[int]:
    return [x[0] for x in struct.iter_unpack('<h', data[1])]


def unpack_s32v(data) -> list[int]:
    return [x[0] for x in struct.iter_unpack('<i', data[1])]


def unpack_u16v(data) -> list[int]:
    return [x[0] for x in struct.iter_unpack('<H', data[1])]


def unpack_u32v(data) -> list[int]:
    return [x[0] for x in struct.iter_unpack('<I', data[1])]


def unpack_f32(data) -> list[float]:
    return [x[0] for x in struct.iter_unpack('<f', data[1])]


def unpack_c64(data) -> list[complex]:
    return [complex(r, i) for (r, i) in struct.iter_unpack('<ff', data[1])]


def unpack_error(data):
    raise RacsException(data[1])


def unpack(b):
    data = msgpack.unpackb(b)

    tp = data[0]
    if tp == "bool":
        return unpack_bool(data)
    if tp == "string":
        return unpack_str(data)
    if tp == "error":
        return unpack_error(data)
    if tp == "int":
        return unpack_int(data)
    if tp == "float":
        return unpack_float(data)
    if tp == "null":
        return unpack_null(data)
    if tp == "list":
        return unpack_list(data)
    if tp == "u8v" or tp == "s8v":
        return unpack_u8v(data)
    if tp == "s16v":
        return unpack_s16v(data)
    if tp == "u16v":
        return unpack_u16v(data)
    if tp == "s32v":
        return unpack_s32v(data)
    if tp == "u32v":
        return unpack_u32v(data)
    if tp == "f32v":
        return unpack_f32(data)
    if tp == "c64v":
        return unpack_c64(data)
    return None
