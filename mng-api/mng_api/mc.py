from mcstatus import JavaServer
import asyncio
import rcon.source
import traceback

from datetime import datetime, UTC


__all__ = ("StatusCheckLoop", "RconClient")


class StatusCheckLoop:
    online_users: list[str]
    latency: int
    last_check: datetime | None
    status_failing: bool

    def __init__(self, address: str, frequency: int = 15, unreachable_factor: int = 2):
        self._address = address
        self._frequency = frequency
        self._unreachable_factor = unreachable_factor

        self.online_users: list[str] = []
        self.latency: int = 99999
        self.last_check = None
        self.status_failing = False

    async def start(self):
        assert self._address, "No address provided, can't begin loop"
        server = await JavaServer.async_lookup(self._address)
        keep_running = True
        while keep_running:
            try:
                # use sync status check, to avoid latency being picked up from coroutine overhead
                status = server.status()
                self.status_failing = False
                self.last_check = datetime.now(UTC)
                self.online_users = [p.name for p in (status.players.sample or [])]
                self.latency = round(status.latency)
            except asyncio.CancelledError:
                keep_running = False
            except (ConnectionRefusedError, TimeoutError, asyncio.TimeoutError):
                self.status_failing = True
            except Exception as e:
                self.status_failing = True
                print(f"Unknown exception: {e}")
                traceback.print_exc()
            await asyncio.sleep(self._frequency)

    def is_reachable(self) -> bool:
        return self.last_check is not None and self.status_failing is False


class RconClient:
    def __init__(self, address: str, port: int, password: str | None = None):
        self._address = address
        self._port = port
        self._password = password

    def _client(self):
        return rcon.source.Client(self._address, self._port, passwd=self._password)

    async def allow_user(self, username: str) -> bool:
        assert " " not in username, "Username cannot contain spaces"
        with self._client() as client:
            response = client.run("whitelist", "add", username).strip()
        print("rcon allow:", response)
        return (
            response.startswith("Added") and response.endswith("to the whitelist")
            or response == "Player is already whitelisted"
        )

    async def remove_user(self, username: str) -> bool:
        assert " " not in username, "Username cannot contain spaces"
        with self._client() as client:
            response = client.run("whitelist", "remove", username).strip()
        print("rcon remove:", response)
        return (
            response.startswith("Removed") and response.endswith("from the whitelist")
            or response == "Player is not whitelisted"
        )
