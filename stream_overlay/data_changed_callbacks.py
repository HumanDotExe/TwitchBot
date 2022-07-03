import asyncio
import logging

from data_types.stream_overlay.types import ActionType

log = logging.getLogger(__name__)


def chat_queue_callback(chat_queue, action, message):
    log.debug(f"chat callback called with action {action} and message {message}")
    if chat_queue is not None:
        data = {"type": action.name}
        if action is ActionType.UPDATE:
            data["messages"] = chat_queue.get_messages_as_json(0)
        elif action is ActionType.ADD:
            data["message"] = message.to_dict()
        for ws in chat_queue.websockets:
            asyncio.get_event_loop().create_task(ws.send_json(data))
