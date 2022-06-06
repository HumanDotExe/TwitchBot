from __future__ import annotations

import importlib
import inspect
from typing import TYPE_CHECKING

from twitchio.ext import commands

import chat_bot
from data_types.types_collection import ChatBotModuleType

if TYPE_CHECKING:
    from data_types.command import Command


class CustomCog(commands.Cog):

    @staticmethod
    def get_commands():
        names = []
        for module_type in ChatBotModuleType:
            if module_type is ChatBotModuleType.CUSTOM or module_type is ChatBotModuleType.BEATSABER:
                pass
            module = importlib.import_module(module_type.value)
            for x in module.__dict__:
                attr = getattr(module, x)
                if inspect.isclass(attr) and issubclass(attr, CustomCog) and attr is not CustomCog:
                    for name, method in inspect.getmembers(attr):
                        if isinstance(method, commands.Command):
                            names.append(name)
        return names

    def __init__(self, bot: chat_bot.ChatBot):
        self.bot = bot

    def add_command(self, command: commands.Command):
        self.bot.add_command(command)
        self._commands[command.name] = command

    def remove_command(self, command_name: str):
        self.bot.remove_command(command_name)
        self._commands.pop(command_name)

    @staticmethod
    def has_user_right(ctx: commands.Context, command: Command) -> bool:
        return command.user_command or command.moderator_command and ctx.author.is_mod or command.broadcaster_command and ctx.author.is_broadcaster

