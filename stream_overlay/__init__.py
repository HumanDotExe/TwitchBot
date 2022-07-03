from __future__ import annotations

import pathlib

from aiohttp import web
import logging

from stream_overlay.data_changed_callbacks import chat_queue_callback
from stream_overlay.overlay_callbacks import chat_overlay_handler

log = logging.getLogger(__name__)


class StreamOverlay:
    __stream_overlay = None

    @classmethod
    def set_stream_overlay(cls, stream_overlay: StreamOverlay):
        cls.__stream_overlay = stream_overlay

    @classmethod
    def get_stream_overlay(cls) -> StreamOverlay:
        return cls.__stream_overlay

    def __init__(self, path: str = "/display"):
        from data_types.stream import Stream
        log.debug("Stream Overlay object created")

        for stream in Stream.get_streams():
            log.debug(f"Initiate chat queue for stream {stream.streamer}")
            stream.initiate_chat_queue(chat_queue_callback)

        self._path = path
        self._app = web.Application()

        self.static_path = pathlib.Path(__file__).resolve().parent / 'static'

        self._app.add_routes([web.static('/static', self.static_path, name="static")])

        for channel in Stream.get_channels():
            self._app.add_routes([web.get(path + "/chat/" + channel.lower(), chat_overlay_handler)])

        self._runner = web.AppRunner(self._app)
        self._site = None

    async def start_stream_overlay(self, host: str, port: int):
        log.info("Starting Stream Overlay")
        await self._runner.setup()
        log.debug("Runner started")
        self._site = web.TCPSite(self._runner, host, port)
        await self._site.start()
        log.debug("Site started")

    async def stop_stream_overlay(self):
        from data_types.stream import Stream
        log.info("Stopping Stream Overlay")
        for stream in Stream.get_streams():
            log.debug(f"Closing open chat websockets for {stream.streamer}:")
            total = 0
            for socket in stream.chat_queue.websockets:
                total += 1
                await socket.close()
            log.debug(f"{total} websockets closed")
        log.debug("Starting cleanup")
        await self._runner.cleanup()
        log.debug("Cleanup done (Stopped site and runner)")

    @property
    def app(self):
        return self._app

