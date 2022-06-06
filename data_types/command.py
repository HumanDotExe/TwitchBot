from __future__ import annotations

import logging
from random import randint
from typing import Optional, TYPE_CHECKING

from chat_bot.custom_cog import CustomCog
from data_types.command_file import CommandConfig

if TYPE_CHECKING:
    from pathlib import Path

log = logging.getLogger(__name__)


class Command:
    __builtin_commands = None

    def __init__(self, file_path: Path):
        log.info(f"Loading command {file_path.name}")
        if self.__builtin_commands is None:
            self.__builtin_commands = CustomCog.get_commands()
        self.__file_path = file_path

        command_config = CommandConfig.load_command_file(file_path)
        self.__command_config = command_config
        self.__is_custom = self.name not in self.__builtin_commands

    def get_message(self, message_type: str = None) -> str:
        if type(self.__command_config["output"]["message"]) is dict:
            if message_type in self.__command_config["output"]["message"]:
                return self.__get_message(self.__command_config["output"]["message"][message_type])
            else:
                log.warning(f"No message for '{message_type}' found")
        else:
            return self.__get_message(self.__command_config["output"]["message"])

    def __get_message(self, message: Optional[str, list]) -> str:
        if type(message) is str:
            return message
        if type(message) is list:
            return self.__get_message_from_list(message)

    def __get_message_from_list(self, message_list: list) -> str:
        if self.__command_config["output"]["random"]:
            return message_list[randint(0, len(message_list) - 1)]
        else:
            return message_list[0]

    @property
    def name(self) -> str:
        return self.__command_config["name"]

    @property
    def user_command(self) -> bool:
        return self.__command_config["rights"]["user"]

    @property
    def moderator_command(self) -> bool:
        return self.__command_config["rights"]["moderator"]

    @property
    def broadcaster_command(self) -> bool:
        return self.__command_config["rights"]["broadcaster"]

    @property
    def is_custom_command(self) -> bool:
        return self.__is_custom
