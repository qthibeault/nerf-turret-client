from dataclasses import dataclass
from typing import Protocol, Type, TypeVar

import msgpack
from typing_extensions import Self


class Msg(Protocol):
    def to_dict(self) -> dict[str, object]:
        ...

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        ...


def _check_msg_type(msg: dict[str, object], expected: str):
    try:
        msg_type = d["type"]
    except KeyError:
        raise ValueError("No message type provided")

    if msg_type != "move":
        raise ValueError(f"Wrong message type {msg_type}")


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

        try:
            base_angle = d["base_angle"]
            elev_angle = d["elev_angle"]
        except KeyError:
            raise ValueError("Missing base or elevation angle")

        if not isinstance(base_angle, float) or not isinstance(elev_angle, float):
            raise TypeError("angle values must be floats")

        return cls(base_angle, elev_angle)


@dataclass()
class ShootMsg(Msg):
    times: int

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "shoot",
            "times": self.times,
        }

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "shoot")

        try:
            times = d["times"]
        except KeyError:
            raise ValueError("Missing number of times to shoot")

        if not isinstance(times, int):
            raise TypeError("times must be an integer")

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

    def to_dict(self) -> dict[str, object]:
        return {"type": "address", "port": self.port}

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        _check_msg_type(d, "address")

        try:
            port = d["port"]
        except KeyError:
            raise ValueError("No port provided")

        if not isinstance(port, int):
            raise TypeError("Port must be an integer")

        return cls(port)


def encode(msg: Msg) -> bytes:
    return msgpack.packb(msg.to_dict())


M = TypeVar("M", bound=Msg)


def decode(bs: bytes, msg_type: Type[M]) -> M:
    return msg_type.from_dict(msgpack.unpackb(bs))
