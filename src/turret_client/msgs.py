from __future__ import annotations

from dataclasses import dataclass
from typing import Type, TypeVar

import msgpack
from typing_extensions import Protocol, Self


class Msg(Protocol):
    def to_dict(self) -> dict[str, object]:
        ...

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> Self:
        ...


def _check_msg_type(msg: dict[str, object], expected: str):
    try:
        msg_type = msg["type"]
    except KeyError:
        raise ValueError("No message type provided")

    if msg_type != expected:
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

        try:
            base_angle = d["base_angle"]
            elev_angle = d["elevation_angle"]
            shots = d["shots"]
        except KeyError:
            raise ValueError(
                "base_angle, elevation_angle, or shots property missing from status message"
            )

        if not isinstance(base_angle, float) or not isinstance(elev_angle, float):
            raise TypeError("Angles must be given as floats")

        if not isinstance(shots, int):
            raise TypeError("Shot counter must be an int")

        return cls(base_angle, elev_angle, shots)


class ResetMsg(Msg):
    def to_dict(self) -> dict[str, object]:
        return {"type": "reset"}

    @classmethod
    def from_dict(cls, d: dict[str, object]):
        _check_msg_type(d, "reset")
        return cls()


def encode(msg: Msg) -> bytes:
    return msgpack.packb(msg.to_dict())


M = TypeVar("M", bound=Msg)


def decode(bs: bytes, msg_type: Type[M]) -> M:
    return msg_type.from_dict(msgpack.unpackb(bs))
