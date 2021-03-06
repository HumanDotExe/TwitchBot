from __future__ import annotations

from typing import Optional

from aiohttp import web
import logging

from beatsaber_request_websocket.beatsaber_integration_callbacks import websocket_handler

log = logging.getLogger(__name__)


class BeatSaberIntegrationCallbacks:
    pass


class BeatSaberIntegration:
    __beatsaber = None

    @classmethod
    def set_beatsaber(cls, beatsaber: BeatSaberIntegration) -> None:
        cls.__beatsaber: BeatSaberIntegration = beatsaber

    @classmethod
    def get_beatsaber(cls) -> BeatSaberIntegration:
        return cls.__beatsaber

    def __init__(self, path: str = "/beatsaber") -> None:
        from data_types.stream import Stream
        log.debug("Beat Saber integration object created")

        self._path: str = path

        self._app: web.Application = web.Application()

        for channel in Stream.get_channels():
            self._app.add_routes([web.get(path + "/" + channel.lower(), websocket_handler)])

        self._runner: web.AppRunner = web.AppRunner(self._app)
        self._site: Optional[web.TCPSite] = None

    async def start_beatsaber_integration(self, host: str, port: int) -> None:
        log.info("Starting Beat Saber Integration")
        await self._runner.setup()
        log.debug("Runner started")
        self._site = web.TCPSite(self._runner, host, port)
        await self._site.start()
        log.debug("Site started")

    async def stop_beatsaber_integration(self) -> None:
        from data_types.stream import Stream
        log.info("Stopping Beat Saber Integration")
        for stream in Stream.get_streams():
            await stream.beatsaber_websocket.close()
        await self._runner.cleanup()
        log.debug("Cleanup done (Stopped site and runner)")

    @property
    def app(self):
        return self._app

