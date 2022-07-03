from __future__ import annotations

import copy
from datetime import datetime
from typing import Callable, List

from data_types.stream_overlay.chat_message import ChatMessage
from data_types.stream_overlay.types import ActionType


class ChatQueue:
    def __init__(self, callback: Callable[[ChatQueue, ActionType, ChatMessage | None], None], include_bot_messages: bool):
        self.__messages: List[ChatMessage] = []
        self.__callback = callback
        self.__include_bot_messages = include_bot_messages
        self.websockets = []

    def update_queue_settings(self, include_bot_messages: bool):
        self.__include_bot_messages = include_bot_messages

    def add_message(self, message_content: str, timestamp: datetime, tags: dict, is_bot_message: bool = False):
        if is_bot_message:
            if not self.__include_bot_messages:
                return
        self.__add_message(ChatMessage(message_content, timestamp, tags))

    def remove_message(self, message_content: str, user: str, sent_at: datetime = None):
        """Completely removes the chat message from the list as if it was never there"""
        message = self.__find_message(message_content, user, sent_at)
        if message:
            self.__remove_message(message)

    def mark_message_as_deleted(self, message_content: str, user: str):
        """Marks a chat message as deleted for display purposes. Intended to be called if a mod deletes a message"""
        message = self.__find_message(message_content, user)
        if message:
            message.delete()
            self.__update_message(message)

    def mark_user_as_deleted(self, user: str):
        """delete all messages written by user. Intended to delete messages on ban"""
        for message in self.__messages:
            if message.user is user:
                message.delete()
                self.__update_message(message)

    def clear(self):
        """clears the chat queue"""
        self.__messages = []
        self.__callback(self, ActionType.CLEAR, None)

    def get_messages(self, number: int = 0):
        return copy.deepcopy(self.__messages[-number:])

    def get_messages_as_json(self, number: int = 0):
        return [m.to_dict() for m in copy.deepcopy(self.__messages[-number:])]

    def __add_message(self, message: ChatMessage):
        self.__messages.append(message)
        self.__callback(self, ActionType.ADD, message)

    def __remove_message(self, message: ChatMessage):
        self.__messages.remove(message)
        self.__callback(self, ActionType.REMOVE, message)

    def __update_message(self, message: ChatMessage):
        self.__callback(self, ActionType.UPDATE, message)

    def __find_message(self, message_content: str, user: str, sent_at: datetime = None) -> ChatMessage | None:
        for message in self.__messages:
            if message.user is user and message.message is message_content and sent_at is not None and message.sent_at == sent_at:
                return message
        return None

