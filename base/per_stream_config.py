from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field
from twitchAPI.type import AuthScope

from utils.alias_generators import to_dash
from utils.string_and_dict_operations_v1 import clean_empty

log = logging.getLogger(__name__)


def load_config(config_file: Path):
    log.debug(f"Loading config for streamer {config_file.parent.name}")
    with open(config_file, 'r') as file:
        config: PerStreamConfig = PerStreamConfig.model_validate(yaml.safe_load(file))

    config.path = config_file
    return config


class Parent(BaseModel):
    model_config = ConfigDict(alias_generator=to_dash, validate_assignment=True)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        log.debug(f"{key} - {value}")
        if isinstance(self, PerStreamConfig) and key != "path" and PerStreamConfig:
            log.debug("root instance, saving")
            self.save()
        else:
            log.debug("not root element")
            # TODO: figure out how to save this


class PopupOverlayConfig(BaseModel):
    message: str
    image: str | None = None
    sound: str | None = None


class NotificationsOverlayConfig(Parent):
    cooldown: int
    follow: PopupOverlayConfig
    subscription: PopupOverlayConfig


class ChatOverlyConfig(Parent):
    include_commands: bool
    include_command_output: bool
    message_stays_for: int
    message_refresh_rate: int
    max_number_of_messages: int
    bot_color: str | None = None


class StreamOverlayConfig(Parent):
    enabled: bool
    block: list[str] = []
    notifications: NotificationsOverlayConfig
    chat: ChatOverlyConfig


class ChatBotConfig(Parent):
    enabled: bool
    save_chatlog: bool
    enable_channel_edit_commands: bool = False
    online_message: str = ""
    offline_message: str = ""
    ignore_commands: list[str] = []


class PerStreamConfig(Parent):
    refresh_token: str
    chat_bot: ChatBotConfig
    stream_overlays: StreamOverlayConfig
    path: Path = Field(None, exclude=True)

    def get_required_auth_scope(self):
        auth_scope = []

        if self.stream_overlays.enabled:
            auth_scope.append(AuthScope.MODERATOR_READ_FOLLOWERS)  # follow events
            auth_scope.append(AuthScope.CHANNEL_READ_SUBSCRIPTIONS)  # sub events

        return auth_scope

    def save(self):
        PerStreamConfig.save_config(self.path, self)

    @staticmethod
    def save_config(path: Path, config: PerStreamConfig):
        with open(path, 'w') as file:
            cleaned = clean_empty(config.model_dump(by_alias=True))
            yaml.safe_dump(cleaned, file, sort_keys=False)
