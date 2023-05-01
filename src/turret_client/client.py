import socket
import warnings

import turret_client.msgs as msgs


def _discover_server() -> tuple[str, int]:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        msg = msgs.DiscoverMsg()
        msg_bytes = msgs.encode(msg)
        sock.sendto(msg_bytes, ("255.255.255.255", 12346))

        data, addr = sock.recvfrom(1024)
        resp = msgs.decode(data, msgs.AddrMsg)

    return addr[0], resp.port


class TurretClient:
    def __init__(self, addr: tuple[str, int] | None = None):
        if addr is None:
            addr = _discover_server()

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect(addr)

    def move(self, base_angle: float, elev_angle: float) -> None:
        msg = msgs.MoveMsg(base_angle, elev_angle)
        msg_bytes = msgs.encode(msg)
        self._sock.send(msg_bytes)

        resp_bytes = self._sock.recv(1024)

        try:
            msgs.decode(resp_bytes, msgs.AckMsg)
        except:
            warnings.warn("Ack message not recieved after sending move command")

    def shoot(self, n: int = 1) -> None:
        msg = msgs.ShootMsg(n)
        msg_bytes = msgs.encode(msg)
        self._sock.send(msg_bytes)

        resp_bytes = self._sock.recv(1024)

        try:
            msgs.decode(resp_bytes, msgs.AckMsg)
        except:
            warnings.warn("Ack message not recieved after sending shoot command")


__all__ = ["TurretClient"]
