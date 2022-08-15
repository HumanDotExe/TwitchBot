from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Optional

from data_types.chat_message import ChatMessage
from data_types.notification_resource import NotificationResource
from data_types.per_stream_config import PerStreamConfig
from data_types.types_collection import NotificationType, ValidationException

if TYPE_CHECKING:
    from uuid import UUID
    from pathlib import Path
    from data_types.types_collection import EventSubType, PubSubType
    from aiohttp.web_ws import WebSocketResponse
    from twitch_api.twitch_user_api import TwitchUserAPI
    from data_types.command import Command

log = logging.getLogger(__name__)


class Stream:
    __command_suffix: str = ".cmd"
    __streams: dict[str, Stream] = dict()

    @classmethod
    def get_stream(cls, streamer: str) -> Optional[Stream]:
        if streamer.lower() in cls.__streams:
            return cls.__streams[streamer.lower()]
        return None

    @classmethod
    def add_stream(cls, stream: Stream) -> None:
        cls.__streams[stream.streamer.lower()] = stream

    @classmethod
    def get_channels(cls) -> list[str]:
        return [channel for channel in cls.__streams.keys()]

    @classmethod
    def get_streams(cls) -> list[Stream]:
        return [stream for stream in cls.__streams.values()]

    def __init__(self, streamer: str, user_id: str, base_path: Path) -> None:
        self.streamer: str = streamer
        self.user_id: str = user_id

        self.__is_streaming: bool = False
        self.__category: Optional[str] = None
        self.__title: Optional[str] = None
        self.__is_mature: Optional[bool] = None
        self.__language: Optional[str] = None

        self.__twitch_user_api: Optional[TwitchUserAPI] = None

        self.config: dict = dict()
        self.__notifications: dict[NotificationType, NotificationResource] = dict()
        self.commands: dict[str, Command] = dict()

        self.__chat_messages: list[ChatMessage] = []

        self.__stream_start: Optional[datetime.datetime] = None
        self.__current_cooldown: int = 0
        self.queue: list[tuple[str, NotificationType]] = []
        self.ban_queue: list[str] = []
        self.active_callbacks: dict[EventSubType, str] = dict()
        self.active_pubsub_uuids: dict[PubSubType, UUID] = dict()

        self._beatsaber_websocket: Optional[WebSocketResponse] = None

        self.paths: dict[str, Path] = {"base": base_path}
        self.paths["stream"] = self.paths["base"] / self.streamer.lower()
        self.paths["resources"] = self.paths["stream"] / "resources"
        self.paths["config"] = self.paths["stream"] / "config.yaml"
        self.load_resources_and_settings()

    def load_resources_and_settings(self) -> None:
        log.info(f"Loading Stream resources for {self.streamer}")

        self.__notifications = {}

        if self.paths["config"].is_file():
            log.debug(f"Config file found")
            self.config = PerStreamConfig.load_config(self.paths["config"])
        else:
            log.debug(f"Using default stream config")
            self.config = PerStreamConfig.load_config(self.paths["base"] / "default.yaml")

        self.__setup_notifications()

        if self.config['chat-bot']['enabled']:
            if self.config['chat-bot']['save-chatlog']:
                self.paths["chatlog"] = self.paths["stream"] / "logs"
                self.paths["chatlog"].mkdir(parents=True, exist_ok=True)
            self.__setup_commands()

    def save_settings(self) -> None:
        log.info(f"Saving Stream settings for {self.streamer}")

        PerStreamConfig.save_config(self.paths["config"], self.config)

    def get_twitch_user_api(self) -> Optional[TwitchUserAPI]:
        return self.__twitch_user_api

    def set_twitch_user_api(self, twitch_api: TwitchUserAPI) -> None:
        self.__twitch_user_api = twitch_api

    def __setup_notifications(self) -> None:
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

    def __setup_commands(self) -> None:
        from data_types.command import Command
        command_files = self.paths["resources"].glob('**/*' + self.__command_suffix)
        for command_file in command_files:
            try:
                command = Command(command_file)
                for name in command.names:
                    self.commands[name] = command
            except ValidationException as e:
                log.warning(f"Problem loading command {command_file.name}: {e}")

    def stream_started(self, start: str) -> None:
        self.__is_streaming = True
        self.__stream_start = datetime.datetime.fromisoformat(start.replace('Z', ''))

    def stream_info_changed(self, title: str, category: str, is_mature: bool, language: str) -> None:
        self.__title = title
        self.__category = category
        self.__is_mature = is_mature
        self.__language = language

    def stream_ended(self) -> None:
        self.__is_streaming = False
        self.__stream_start = None

    def set_callback_id(self, callback_id: str, topic: EventSubType) -> None:
        self.active_callbacks[topic] = callback_id

    def get_callback_id(self, topic: EventSubType) -> str:
        return self.active_callbacks[topic]

    def set_pubsub_uuid(self, uuid: UUID, topic: PubSubType) -> None:
        self.active_pubsub_uuids[topic] = uuid

    def get_pubsub_uuid(self, topic: PubSubType) -> UUID:
        return self.active_pubsub_uuids[topic]

    def add_to_queue(self, name: str, notification_type: NotificationType) -> None:
        for entry in self.config['stream-overlays']['notifications']['block']:
            if entry in name and name not in self.ban_queue:
                self.ban_queue.append(name)
        if name not in self.ban_queue:
            self.queue.append((name, notification_type))

    def get_alert_info(self, notification_type: NotificationType) -> NotificationResource:
        if notification_type in self.__notifications:
            return self.__notifications[notification_type]

    def decrease_cooldown(self) -> None:
        if self.__current_cooldown > 0:
            self.__current_cooldown = self.__current_cooldown - 1

    def reset_cooldown(self) -> None:
        self.__current_cooldown = self.config['stream-overlays']['notifications']['cooldown']

    def write_into_chatlog(self, user: str, message: str) -> None:
        if self.config['chat-bot']['save-chatlog']:
            filename = self.paths["chatlog"] / f"chatlog_{datetime.datetime.now().date().isoformat()}.txt"
            with open(filename, "a+") as f:
                time = datetime.datetime.now().time().isoformat()
                f.write(f"{time}:{user}: {message}\n")

    def add_chat_message(self, message: str, tags: dict[str, dict], is_bot_message: Optional[bool] = False) -> None:
        if is_bot_message:
            if self.config['stream-overlays']['chat']['include-command-output']:
                tags['color'] = self.config['chat-bot']['bot-color']
            else:
                return
        self.__chat_messages.append(ChatMessage(message, self.config['stream-overlays']['chat']['message-stays-for'],
                                                self.config['stream-overlays']['chat']['message-refresh-rate'], tags))

    def remove_chat_message(self, message: ChatMessage) -> None:
        """Completely removes the chat message from the list as if it was never there"""
        self.__chat_messages.remove(message)

    def find_chat_message(self, message: str, user: str) -> ChatMessage | None:
        """Finds the ChatMessage instance"""
        for chat_message in self.__chat_messages:
            if chat_message.user == user and chat_message.message == message:
                return chat_message
        return None

    def delete_all_messages_by_user(self, user: str) -> None:
        """delete all messages written by user. Intended to delete messages on ban"""
        for chat_message in self.__chat_messages:
            if chat_message.user == user:
                chat_message.delete()

    def delete_chat_message(self, message: str, user: str) -> None:
        """Marks a chat message as deleted for display purposes. Intended to be called if a mod deletes a message"""
        chat_message = self.find_chat_message(message, user)
        if chat_message:
            chat_message.delete()

    def clear_chat(self) -> None:
        self.__chat_messages = []

    def set_beatsaber_websocket(self, websocket: WebSocketResponse) -> None:
        self._beatsaber_websocket = websocket

    def get_command(self, command_name: str) -> Command | None:
        if command_name in self.commands:
            return self.commands[command_name]
        return None

    def get_custom_commands(self) -> list[str]:
        return [x.name for x in self.commands.values() if x.is_custom_command]

    @property
    def beatsaber_websocket(self) -> WebSocketResponse | None:
        return self._beatsaber_websocket

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
    def is_mature(self):
        return self.__is_mature

    @property
    def language(self):
        return self.__language

    @property
    def uptime(self):
        if self.__is_streaming:
            return datetime.datetime.utcnow() - self.__stream_start
        return None

    @property
    def chat_messages(self):
        return self.__chat_messages
