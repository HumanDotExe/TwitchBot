from __future__ import annotations

import logging

from aiohttp import web

from webserver.independent_display import display_time
from webserver.per_stream_display import display_uptime, display_notifications

log = logging.getLogger(__name__)


class Webserver:
    __webserver = None

    @classmethod
    def set_webserver(cls, webserver: Webserver):
        cls.__webserver = webserver

    @classmethod
    def get_webserver(cls) -> Webserver:
        return cls.__webserver

    def __init__(self, path: str = "/display"):
        log.debug("Webserver Object Created")
        self._path = path
        self._app = web.Application()
        self._app.add_routes([web.get(path + "/time" + '{tail:.*}', display_time),
                              web.get(path + "/uptime" + '{tail:.*}', display_uptime),
                              web.get(path + "/notifications" + '{tail:.*}', display_notifications)])
        self._runner = web.AppRunner(self._app)
        self._site = None

    async def start_webserver(self, host: str, port: int):
        log.info("Starting Webserver")
        await self._runner.setup()
        log.debug("Runner started")
        self._site = web.TCPSite(self._runner, host, port)
        await self._site.start()
        log.debug("Site started")

    async def stop_webserver(self):
        log.info("Stopping Webserver")
        await self._runner.cleanup()
        log.debug("Cleanup done (Stopped site and runner)")

    @property
    def app(self):
        return self._app
