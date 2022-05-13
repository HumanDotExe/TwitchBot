from __future__ import annotations

import datetime
import logging
import pathlib
from typing import Union, List
from uuid import UUID

from data_types.chat_message import ChatMessage
from data_types.notification_resource import NotificationResource
from data_types.per_stream_config import PerStreamConfig
from data_types.types_collection import NotificationType, EventSubType, PubSubType

log = logging.getLogger(__name__)


class Stream:
    __command_suffix = ".cmd"
    __streams = {}

    @classmethod
    def get_stream(cls, streamer: str) -> Union[None, Stream]:
        if streamer.lower() in cls.__streams:
            return cls.__streams[streamer.lower()]
        return None

    @classmethod
    def add_stream(cls, stream: Stream):
        cls.__streams[stream.streamer.lower()] = stream

    @classmethod
    def get_channels(cls) -> List[str]:
        return [channel for channel in cls.__streams.keys()]

    @classmethod
    def get_streams(cls) -> List[Stream]:
        return [stream for stream in cls.__streams.values()]

    def __init__(self, streamer: str, user_id: str, base_path: pathlib.Path):
        self.chat_overlay_settings = None
        self.streamer = streamer
        self.user_id = user_id

        self.__is_streaming = False
        self.__category = None
        self.__title = None
        self.__is_mature = None
        self.__language = None

        self.config = None
        self.__notifications = {}
        self.commands = {}

        self.__chat_messages = []

        self.__stream_start = None
        self.__current_cooldown = 0
        self.queue = []
        self.ban_queue = []
        self.active_callbacks = {}
        self.active_pubsub_uuids = {}

        self.paths = {"base": base_path}
        self.paths["stream"] = self.paths["base"] / self.streamer.lower()
        self.paths["resources"] = self.paths["stream"] / "resources"
        self.load_resources_and_settings()

    def load_resources_and_settings(self):
        log.info(f"Loading Stream resources for {self.streamer}")

        self.__notifications = {}

        config_path = self.paths["stream"] / "config.yaml"
        if config_path.is_file():
            log.debug(f"Config file found")
            self.config = PerStreamConfig.load_config(config_path)
        else:
            log.debug(f"Using default stream config")
            self.config = PerStreamConfig.load_config(self.paths["base"] / "default.yaml")

        self.__setup_notifications()

        if self.config['chat-bot']['enabled']:
            if self.config['chat-bot']['save-chatlog']:
                self.paths["chatlog"] = self.paths["stream"] / "logs"
                self.paths["chatlog"].mkdir(parents=True, exist_ok=True)
            self.__setup_custom_commands()

    def __setup_notifications(self):
        notifications = self.config['stream-overlays']['notifications']
        for notification_type in NotificationType:
            self.__notifications[notification_type] = NotificationResource(notification_type)
            self.__notifications[notification_type].set_message(notifications[notification_type.value]['message'])
            image_name = notifications[notification_type.value]['image']
            if image_name:
                self.__notifications[notification_type].set_image(image_name, self.paths["resources"])
            sound_name = notifications[notification_type.value]['sound']
            if sound_name:
                self.__notifications[notification_type].set_sound(sound_name, self.paths["resources"])

    def __setup_custom_commands(self):
        command_files = self.paths["resources"].glob('**/*' + self.__command_suffix)
        for command in command_files:
            self.commands[command.name.replace(self.__command_suffix, '')] = command.read_text()

    def stream_started(self, start: str):
        self.__is_streaming = True
        self.__stream_start = datetime.datetime.fromisoformat(start.replace('Z', ''))

    def stream_info_changed(self, title: str, category: str, is_mature: bool, language: str):
        self.__title = title
        self.__category = category
        self.__is_mature = is_mature
        self.__language = language

    def stream_ended(self):
        self.__is_streaming = False
        self.__stream_start = None

    def set_callback_id(self, callback_id: str, topic: Union[EventSubType]):
        self.active_callbacks[topic] = callback_id

    def get_callback_id(self, topic: Union[EventSubType]) -> str:
        return self.active_callbacks[topic]

    def set_pubsub_uuid(self, uuid: UUID, topic: Union[PubSubType]):
        self.active_pubsub_uuids[topic] = uuid

    def get_pubsub_uuid(self, topic: Union[PubSubType]) -> UUID:
        return self.active_pubsub_uuids[topic]

    def add_to_queue(self, name: str, notification_type: NotificationType):
        for entry in self.config['stream-overlays']['notifications']['block']:
            if entry in name and name not in self.ban_queue:
                self.ban_queue.append(name)
        if name not in self.ban_queue:
            self.queue.append((name, notification_type))

    def get_alert_info(self, notification_type: NotificationType):
        if notification_type in self.__notifications:
            return self.__notifications[notification_type]

    def decrease_cooldown(self):
        if self.__current_cooldown > 0:
            self.__current_cooldown = self.__current_cooldown - 1

    def reset_cooldown(self):
        self.__current_cooldown = self.config['stream-overlays']['notifications']['cooldown']

    def write_into_chatlog(self, user: str, message: str):
        if self.config['chat-bot']['save-chatlog']:
            filename = self.paths["chatlog"] / f"chatlog_{datetime.datetime.now().date().isoformat()}.txt"
            with open(filename, "a+") as f:
                time = datetime.datetime.now().time().isoformat()
                f.write(f"{time}:{user}: {message}\n")

    def add_chat_message(self, message: str, tags: dict):
        self.__chat_messages.append(ChatMessage(message, self.config['stream-overlays']['chat']['message-stays-for'], self.config['stream-overlays']['chat']['message-refresh-rate'], tags))

    def remove_chat_message(self, message: ChatMessage):
        """Completely removes the chat message from the list as if it was never there"""
        self.__chat_messages.remove(message)

    def find_chat_message(self, message: str, user: str) -> Union[ChatMessage, None]:
        """Finds the ChatMessage instance"""
        for chat_message in self.__chat_messages:
            if chat_message.user == user and chat_message.message == message:
                return chat_message
        return None

    def delete_all_messages_by_user(self, user: str):
        """delete all messages written by user. Intended to delete messages on ban"""
        for chat_message in self.__chat_messages:
            if chat_message.user == user:
                chat_message.delete()

    def delete_chat_message(self, message: str, user: str):
        """Marks a chat message as deleted for display purposes. Intended to be called if a mod deletes a message"""
        chat_message = self.find_chat_message(message, user)
        if chat_message:
            chat_message.delete()


    def clear_chat(self):
        self.__chat_messages = []

    @property
    def current_cooldown(self):
        return self.__current_cooldown

    @property
    def title(self):
        return self.__title

    @property
    def game(self):
        return self.__category

    @property
    def is_live(self):
        return self.__is_streaming

    @property
    def uptime(self):
        if self.__is_streaming:
            return datetime.datetime.utcnow() - self.__stream_start
        return None

    @property
    def chat_messages(self):
        return self.__chat_messages
