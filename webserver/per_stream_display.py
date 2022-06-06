from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiohttp import web

from data_types.stream import Stream
from utils import timedelta

if TYPE_CHECKING:
    from aiohttp.web_request import Request

log = logging.getLogger(__name__)

default_html = "<html><head><meta charset=\"UTF-8\"/><meta http-equiv=\"refresh\" content=\"{refresh}\" /></head><body>{content}</body></html>"


async def display_uptime(request: Request):
    if request.rel_url.query.get('stream', '') in Stream.get_channels():
        stream = Stream.get_stream(request.rel_url.query.get('stream', ''))
        uptime = stream.uptime
        if uptime:
            delta = timedelta.format_timedelta(uptime)
            if int(delta['days']) == 1:
                response_html = default_html.format(refresh=30,
                                                    content=f"{delta['days']} day, {delta['hours']}:{delta['minutes']}h")
            elif int(delta['days']) > 1:
                response_html = default_html.format(refresh=30,
                                                    content=f"{delta['days']} days, {delta['hours']}:{delta['minutes']}h")
            else:
                response_html = default_html.format(refresh=30, content=f"{delta['hours']}:{delta['minutes']}h")
        else:
            response_html = default_html.format(refresh=30, content="Offline")
        return web.Response(text=response_html, content_type='text/html')
    return web.Response(text="Error")


async def display_notifications(request: Request):
    if request.rel_url.query.get('stream', '') in Stream.get_channels():
        stream = Stream.get_stream(request.rel_url.query.get('stream', ''))
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
        return web.Response(text=response_html, content_type='text/html')
    return web.Response(text="Error")


async def display_chat_messages(request: Request):
    if request.rel_url.query.get('stream', '') in Stream.get_channels():
        stream = Stream.get_stream(request.rel_url.query.get('stream', ''))
        content = "<div id='chat' width=500px style='{word-break: break-word;}'>"

        # TODO: finish this, this does not look finished
        message_number = stream.config['stream-overlays']['chat']['max-number-of-messages']
        try:
            message_number = int(request.rel_url.query.get('count', 'blah'))
        except ValueError:
            message_number = stream.config['stream-overlays']['chat']['max-number-of-messages']

        if message_number > 0:
            messages = stream.chat_messages[-message_number:]
        else:
            messages = stream.chat_messages

        for message in messages:
            if message.time_left > 0:
                content += f"<p id='chat_message'>{message.chat_message}</p>"
                message.decrease_time_left()
            else:
                stream.remove_chat_message(message)
        content += "</div>"
        return web.Response(
            text=default_html.format(refresh=stream.config['stream-overlays']['chat']['message-refresh-rate'],
                                     content=content), content_type='text/html')
    return web.Response(text="Error")
