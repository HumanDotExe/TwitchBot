import aiohttp
from aiohttp import web

import logging

from aiohttp.web_request import Request

from chat_bot import ChatBot
from data_types.stream import Stream

log = logging.getLogger(__name__)


async def websocket_handler(request: Request):
    stream = None
    for s in Stream.get_streams():
        if s.streamer.lower() == request.rel_url.name:
            stream = s
    if stream:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        stream.set_beatsaber_websocket(ws)
        log.info(f"Beat Saber Websocket connection for stream {stream.streamer} ready")

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                log.debug(msg.data)
                message = str(msg.data).encode('utf-8').decode('utf-8-sig')
                await ChatBot.get_bot().send(message, stream.streamer)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                log.error(f"Beat Saber Websocket for stream {stream.streamer} closed with exception: {ws.exception()}")

    print('Websocket connection closed')
