import os
from typing import Union

from aiohttp import web

from data_types.stream_overlay.types import ActionType

WS_FILE = os.path.join(os.path.dirname(__file__), "static/chat.html")


async def chat_overlay_handler(request: web.Request) -> Union[web.WebSocketResponse, web.FileResponse]:
    from data_types.stream import Stream
    stream = Stream.get_stream(request.rel_url.name)
    if stream:
        resp = web.WebSocketResponse()
        available = resp.can_prepare(request)
        if not available:
            return web.FileResponse(WS_FILE)

        await resp.prepare(request)

        message_number = int(request.rel_url.query.get('number', '0'))
        stays_for = 0

        await resp.send_json({"type": ActionType.UPDATE.name, "messages": stream.chat_queue.get_messages_as_json(message_number)})

        try:
            stream.chat_queue.websockets.append(resp)

            async for _ in resp:
                pass
            return resp

        finally:
            stream.chat_queue.websockets.remove(resp)
