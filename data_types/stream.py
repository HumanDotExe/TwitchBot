from __future__ import annotations

import configparser
import datetime
import logging
import pathlib
from typing import Union, List

from data_types.notification_resource import NotificationResource
from data_types.types_collection import NotificationType, EventSubType

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
        self.streamer = streamer
        self.user_id = user_id

        self.__is_streaming = False
        self.__category = None
        self.__title = None
        self.__is_mature = None
        self.__language = None

        self.__config = None
        self.enable_webserver = None
        self.enable_chat_bot = None
        self.ban_all = None
        self.block_notifications_from = []
        self.ignore_commands = []
        self.save_chatlog = None
        self.__notification_cooldown = None
        self.__notifications = {}
        self.commands = {}

        self.__stream_start = None
        self.__current_cooldown = 0
        self.queue = []
        self.ban_queue = []
        self.active_callbacks = {}

        self.paths = {"base": base_path}
        self.paths["stream"] = self.paths["base"] / self.streamer.lower()
        self.paths["resources"] = self.paths["stream"] / "resources"
        self.load_resources_and_settings()

    def load_resources_and_settings(self):
        log.info(f"Loading Stream resources for {self.streamer}")

        self.__notifications = {}
        self.__notification_cooldown = 3

        config_path = self.paths["stream"] / "config.ini"
        self.__config = configparser.ConfigParser()
        if config_path.is_file():
            log.debug(f"Config file found")
            self.__config.read(config_path)
        else:
            log.debug(f"Using default stream config")
            self.__config.read(self.paths["base"] / "default.ini")

        general = "GENERAL"
        if self.__config.has_section(general):
            self.ban_all = self.__config[general].getboolean("ban-all", fallback=False)
            self.enable_chat_bot = self.__config[general].getboolean("enable-chat-bot", fallback=False)
            self.enable_webserver = self.__config[general].getboolean("enable-webserver", fallback=False)

        notifications = "NOTIFICATIONS"
        if self.enable_webserver:
            if self.__config.has_section(notifications):
                self.__notification_cooldown = self.__config[general].getint("cooldown", fallback=3)
                self.block_notifications_from = self.__config[notifications].get("block", fallback="").split(" ")
                self.__setup_notifications()

        chat = "CHAT"
        if self.enable_chat_bot and self.__config.has_section(chat):
            self.ignore_commands = []
            ignore = self.__config[chat].get("ignore-commands", fallback="")
            self.ignore_commands.extend(ignore.split(" "))
            if "save-chatlog" in self.__config[chat].keys():
                self.save_chatlog = self.__config[chat].getboolean("save-chatlog", fallback=False)
            if self.save_chatlog:
                self.paths["chatlog"] = self.paths["stream"] / "logs"
                self.paths["chatlog"].mkdir(parents=True, exist_ok=True)
            self.__setup_custom_commands()

    def __setup_notifications(self):
        messages = "MESSAGES"
        images = "IMAGES"
        sounds = "SOUNDS"
        for notification_type in NotificationType:
            self.__notifications[notification_type] = NotificationResource(notification_type)
            if self.__config.has_section(messages):
                self.__notifications[notification_type].set_message(
                    self.__config[messages].get(notification_type.value[0], fallback="Thanks {name}!"))
            if self.__config.has_section(images):
                image_name = self.__config[images].get(notification_type.value[0], fallback=None)
                self.__notifications[notification_type].set_image(image_name, self.paths["resources"])
            if self.__config.has_section(sounds):
                sound_name = self.__config[sounds].get(notification_type.value[0], fallback=None)
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

    def get_callback_id(self, topic: Union[EventSubType]):
        return self.active_callbacks[topic]

    def add_to_queue(self, name: str, notification_type: NotificationType):
        for entry in self.block_notifications_from:
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
        self.__current_cooldown = self.__notification_cooldown

    def write_into_chatlog(self, user: str, message: str):
        if self.save_chatlog:
            filename = self.paths["chatlog"] / f"chatlog_{datetime.datetime.now().date().isoformat()}.txt"
            with open(filename, "a+") as f:
                time = datetime.datetime.now().time().isoformat()
                f.write(f"{time}:{user}: {message}\n")

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
