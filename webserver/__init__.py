from __future__ import annotations

import datetime
import logging

from aiohttp import web

from aiohttp.web_request import Request

from utils import timedelta
from data_types.stream import Stream

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
        self._app.router.add_get(path+'{tail:.*}', self.display)
        self._runner = web.AppRunner(self._app)
        self._site = None

    async def display(self, request: Request):
        default_html = "<html><head><meta charset=\"UTF-8\"/><meta http-equiv=\"refresh\" content=\"{refresh}\" /></head><body>{content}</body></html>"
        action = request.path.replace(self._path, "").strip("/")
        response_html = -1

        # actions that don't care about which stream they display
        if action == "time":
            response_html = default_html.format(refresh=1, content=f"{datetime.datetime.now().strftime('%H:%M:%S')}")

        # stream dependent actions
        if request.query_string in Stream.get_channels():
            stream = Stream.get_stream(request.query_string)
            if action == "uptime":
                uptime = stream.uptime
                if uptime:
                    delta = timedelta.format_timedelta(uptime)
                    if int(delta['days']) == 1:
                        response_html = default_html.format(refresh=30, content=f"{delta['days']} day, {delta['hours']}:{delta['minutes']}h")
                    elif int(delta['days']) > 1:
                        response_html = default_html.format(refresh=30, content=f"{delta['days']} days, {delta['hours']}:{delta['minutes']}h")
                    else:
                        response_html = default_html.format(refresh=30, content=f"{delta['hours']}:{delta['minutes']}h")
                else:
                    response_html = default_html.format(refresh=30, content="Offline")
            elif action == "notifications":
                if len(stream.queue) > 0 and stream.current_cooldown == 0:
                    content = "<div id='queue_display'>"
                    name, notification_type = stream.queue.pop()
                    notification_resource = stream.get_alert_info(notification_type)
                    if notification_resource.has_image():
                        image, image_mime = notification_resource.get_image()
                        content = content + f"<img src=\"data:{image_mime};base64,{image}\">"
                    if notification_resource.has_sound():
                        sound, sound_mime = notification_resource.get_sound()
                        content = content + f"<audio autoplay><source type=\"{sound_mime}\"src=\"data:{sound_mime};base64,{sound}\"></audio>"
                    if notification_resource.has_message():
                        formatted_name = f"<span>{name}</span>"
                        message = notification_resource.get_message().format(name=formatted_name)
                        content = content + f"<p id='message'>{message}</p>"
                    content = content + "</div>"
                    response_html = default_html.format(content=content, refresh=10)
                    stream.reset_cooldown()
                else:
                    response_html = default_html.format(refresh=1, content="")
                    stream.decrease_cooldown()

        if response_html == -1:
            return web.Response(text="Error")
        return web.Response(text=response_html, content_type='text/html')

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
