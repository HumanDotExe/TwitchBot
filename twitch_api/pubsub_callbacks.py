import logging
from typing import Union
from uuid import UUID

from data_types.stream import Stream
from data_types.types_collection import ModerationActionType, PubSubType

log = logging.getLogger(__name__)
debug_log = logging.getLogger("debug-logger")


class PubSubCallbacks:

    @staticmethod
    def on_chat_moderator_action(uuid: UUID, data: dict) -> None:
        action = data['data']['moderation_action']
        if action == ModerationActionType.CLEAR:
            stream = PubSubCallbacks.get_stream_for_action(uuid, PubSubType.CHAT_MODERATOR_ACTIONS)
            if stream:
                stream.clear_chat()
        elif action == ModerationActionType.BAN:
            # only delete messages by banned user, multi-ban is handled by eventsub
            stream = PubSubCallbacks.get_stream_for_action(uuid, PubSubType.CHAT_MODERATOR_ACTIONS)
            if stream:
                stream.delete_all_messages_by_user(data['data']['target_user_login'])
        elif action == ModerationActionType.UNBAN:
            # do nothing, multi-unban is handled by eventsub
            pass
        else:
            # there is next to no documentation on this, so I need to collect more data about possible responses
            debug_log.info(f"on_chat_moderator_action callback: {data}", data)

    @staticmethod
    def get_stream_for_action(uuid: UUID, action: PubSubType) -> Union[Stream, None]:
        for s in Stream.get_streams():
            if s.get_pubsub_uuid(action) == uuid:
                return s
        log.warning(f"UUID {uuid} does not belong to any stream but exists")
        return None



