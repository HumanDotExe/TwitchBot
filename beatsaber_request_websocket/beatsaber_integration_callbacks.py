from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiohttp import web, WSMsgType
from simplematch import test, match

if TYPE_CHECKING:
    from aiohttp.web_request import Request

from chat_bot import ChatBot
from data_types.stream import Stream
from data_types.types_collection import BeatSaberMessageType
from utils.string_and_dict_operations import strip_whitespaces

log = logging.getLogger(__name__)
debug = logging.getLogger("debug-logger")


async def websocket_handler(request: Request):
    stream = Stream.get_stream(request.rel_url.name)
    if stream:
        stream.set_beatsaber_websocket(web.WebSocketResponse())
        await stream.beatsaber_websocket.prepare(request)
        log.info(f"Beat Saber Websocket connection for stream {stream.streamer} ready")

        async for msg in stream.beatsaber_websocket:
            log.debug(msg)
            if msg.type == WSMsgType.CLOSED:
                pass
            elif msg.type == WSMsgType.TEXT:
                message = str(msg.data).encode('utf-8').decode('utf-8-sig')
                if message_to_dict(message) is {}:
                    debug.info(f"beatsaber: {message}")
                await ChatBot.get_bot().send(message, stream.streamer)
            elif msg.type == WSMsgType.ERROR:
                log.error(
                    f"Beat Saber Websocket for stream {stream.streamer} closed with exception: {stream.beatsaber_websocket.exception()}")

    print('Websocket connection closed')


template_dict = {
    BeatSaberMessageType.QUEUE_OPEN: "Queue is open.",
    BeatSaberMessageType.QUEUE_CLOSE: "Queue is closed.",
    BeatSaberMessageType.NEXT_SONG: "{song_name}*/{band_name} ({beatsaver_code}) requested by {requester} is next.",
    BeatSaberMessageType.SONG_REMOVED: "{song_name} ({beatsaver_code}) removed.",
    BeatSaberMessageType.QUEUE_OPENED: "Queue is now open.",
    BeatSaberMessageType.QUEUE_CLOSED: "Queue is now closed.",
    BeatSaberMessageType.SONG_ADDED: "Request {song_name}*/{band_name} ({beatsaver_code}) added to queue.",
    BeatSaberMessageType.SONG_ADDED_TOO_MANY_RESULTS: "Request for '{request}}' produces {result_number:int} results*",
    BeatSaberMessageType.SONG_ADDED_NOT_FOUND: "Invalid BeatSaver ID \"{beatsaver_code}\" specified. https://api.beatsaver.com/maps/id/9cc5",
    BeatSaberMessageType.SONG_ADDED_QUEUE_CLOSED: "Queue is currently closed.",
}


def message_to_dict(message: str) -> dict:
    for message_type in BeatSaberMessageType:
        if message_type in template_dict and test(template_dict[message_type], message):
            return strip_whitespaces({**{"type": message_type}, **match(template_dict[message_type], message)})
    return {}
