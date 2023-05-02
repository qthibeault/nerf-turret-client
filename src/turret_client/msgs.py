from __future__ import annotations

from abc import ABC, abstractmethod, abstractclassmethod
from dataclasses import dataclass
from typing import Type, TypeVar

import msgpack
from typing_extensions import Self


class MsgError(Exception):
    pass


class Msg(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, object]:
        ...

    @abstractclassmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        ...


class MsgTypeError(MsgError):
    pass


def _check_msg_type(msg: dict[str, object], expected: str):
    try:
        msg_type = msg["type"]
    except KeyError:
        raise MsgTypeError("No message type provided")

    if msg_type != expected:
        raise MsgTypeError(f"Expected message type [{expected}], got [{msg_type}]")


T = TypeVar("T", int, float, str)


class MsgDataError(MsgError):
    pass


def _get_msg_data(msg: dict[str, object], name: str, data_type: Type[T]) -> T:
    try:
        msg_data = msg[name]
    except KeyError:
        raise MsgDataError(f"Missing [{name}] in msg")

    if not isinstance(msg_data, data_type):
        raise MsgDataError(
            f"[{name}] must be type [{data_type}], got [{type(msg_data)}]"
        )

    return msg_data


def _check_int(value: object, name: str, lb: int | None = None) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")

    if lb is not None and value < lb:
        raise ValueError(f"{name} must be greater than {lb}")


@dataclass()
class MoveMsg(Msg):
    base_angle: float
    elev_angle: float

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "move",
            "base_angle": self.base_angle,
            "elev_angle": self.elev_angle,
        }

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "move")
        base_angle = _get_msg_data(d, "base_angle", float)
        elev_angle = _get_msg_data(d, "elev_angle", float)

        return cls(base_angle, elev_angle)


@dataclass()
class ShootMsg(Msg):
    times: int

    def __post_init__(self):
        _check_int(self.times, "times", 0)

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "shoot",
            "times": self.times,
        }

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "shoot")
        times = _get_msg_data(d, "times", int)

        return cls(times)


class AckMsg(Msg):
    def to_dict(self) -> dict[str, object]:
        return {"type": "acknowledge"}

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "acknowledge")
        return cls()


class DiscoverMsg(Msg):
    def to_dict(self) -> dict[str, object]:
        return {"type": "discover"}

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "discover")
        return cls()


@dataclass()
class AddrMsg(Msg):
    port: int

    def __post_init__(self):
        _check_int(self.port, "port", 1)

    def to_dict(self) -> dict[str, object]:
        return {"type": "address", "port": self.port}

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "address")
        port = _get_msg_data(d, "port", int)

        return cls(port)


class RequestStatusMsg(Msg):
    def to_dict(self) -> dict[str, object]:
        return {"type": "statusrequest"}

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "statusrequest")
        return cls()


@dataclass()
class StatusMsg(Msg):
    base_angle: float
    elev_angle: float
    shots: int

    def __post_init__(self):
        if isinstance(self.base_angle, int):
            self.base_angle = float(self.base_angle)

        if not isinstance(self.base_angle, float):
            raise TypeError("base angle must be a float")

        if isinstance(self.elev_angle, int):
            self.elev_angle = float(self.elev_angle)

        if not isinstance(self.elev_angle, float):
            raise TypeError("elev angle must be a float")

        _check_int(self.shots, "shots", 0)

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "status",
            "base_angle": self.base_angle,
            "elevation_angle": self.elev_angle,
            "shots": self.shots,
        }

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "status")
        base_angle = _get_msg_data(d, "base_angle", float)
        elev_angle = _get_msg_data(d, "elevation_angle", float)
        shots = _get_msg_data(d, "shots", int)

        return cls(base_angle, elev_angle, shots)


class ResetMsg(Msg):
    def to_dict(self) -> dict[str, object]:
        return {"type": "reset"}

    @classmethod
    def from_dict(cls, d: dict[str, object]):
        _check_msg_type(d, "reset")
        return cls()


def encode(msg: Msg) -> bytes:
    if not isinstance(msg, Msg):
        raise TypeError(f"Can only encode values of type Msg, not [{type(msg)}]")

    return msgpack.packb(msg.to_dict())


M = TypeVar("M", bound=Msg)


class DecodeError(MsgError):
    pass


def decode(bs: bytes, msg_type: Type[M]) -> M:
    msg_data = msgpack.unpackb(bs)

    if not isinstance(msg_data, dict):
        raise DecodeError("message did not unpack into dictionary")

    return msg_type.from_dict(msgpack.unpackb(bs))
