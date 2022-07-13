from __future__ import annotations

import importlib
import inspect
import logging
import pathlib
import random
from typing import TYPE_CHECKING

from twitchio.ext import commands

import chat_bot
from data_types.types_collection import ChatBotModuleType, ValidationException
from utils import timedelta

if TYPE_CHECKING:
    from data_types.command import Command

log = logging.getLogger(__name__)


class CustomCog(commands.Cog):
    # this import is used by the subclasses of CustomCog
    from data_types.stream import Stream

    global_commands: dict[str, Command] = {}

    @staticmethod
    def get_commands() -> list[str]:
        names = []
        for module_type in ChatBotModuleType:
            if module_type == ChatBotModuleType.CUSTOM or module_type == ChatBotModuleType.BEATSABER:
                pass
            module = importlib.import_module(module_type.value)
            for x in module.__dict__:
                attr = getattr(module, x)
                if inspect.isclass(attr) and issubclass(attr, CustomCog) and attr is not CustomCog:
                    for name, method in inspect.getmembers(attr):
                        if isinstance(method, commands.Command):
                            names.append(name)
        return names

    @classmethod
    def load_global_commands(cls, suffix: str = ".cmd") -> None:
        from data_types.command import Command
        path = pathlib.Path(__file__).resolve().parent / "commands"
        command_files = path.glob('**/*' + suffix)
        for command_file in command_files:
            try:
                command = Command(command_file)
                cls.global_commands[command.name] = command
            except ValidationException as e:
                log.warning(f"Problem loading command {command_file.name}: {e}")

    @classmethod
    def get_command(cls, command_name: str, stream: Stream = None) -> Command | None:
        command = None
        if stream is not None:
            command = stream.get_command(command_name)
        if command is None and command_name in cls.global_commands:
            return cls.global_commands[command_name]
        return command

    def __init__(self, bot: chat_bot.ChatBot) -> None:
        self.bot: chat_bot.ChatBot = bot

    def add_command(self, command: commands.Command) -> None:
        self.bot.add_command(command)
        self._commands[command.name] = command

    def remove_command(self, command_name: str) -> None:
        self.bot.remove_command(command_name)
        self._commands.pop(command_name)

    @staticmethod
    def has_user_right(ctx: commands.Context, command: Command) -> bool:
        return command.user_command or command.moderator_command and ctx.author.is_mod or command.broadcaster_command and ctx.author.is_broadcaster

    @staticmethod
    def get_format_dicts(command: Command, ctx: commands.Context, stream: Stream, *args) -> dict:
        return {
            **CustomCog.__create_param_dict(command, ctx.author.display_name, *args),
            **CustomCog.__create_stream_dict(stream),
            **CustomCog.__create_context_dict(ctx),
            **CustomCog.__create_random_dict(command)
        }

    @staticmethod
    def __create_context_dict(ctx: commands.Context) -> dict:
        context_dict = {
            "user": ctx.author.display_name,
            "channel": ctx.channel.name,
            "command": ctx.command.name
        }
        return context_dict

    @staticmethod
    def __create_stream_dict(stream: Stream) -> dict:
        stream_param_dict = {
            "streamer": stream.streamer,
        }
        if stream.is_live:
            stream_param_dict["title"] = stream.title
            stream_param_dict["game"] = stream.game
            if stream.uptime:
                delta = timedelta.format_timedelta(stream.uptime)
                stream_param_dict["uptime_hours"] = delta["hours"]
                stream_param_dict["uptime_minutes"] = delta["minutes"]
        return stream_param_dict

    @staticmethod
    def __create_param_dict(command: Command, user: str,  *args) -> dict:
        param_dict = {}
        for number in range(0, command.parameter_count):
            param = "param" + str(number)
            if len(args) > number:
                param_dict[param] = args[number]
            elif command.replace_param_with_caller(param):
                param_dict[param] = user
            elif not command.is_param_required(param):
                param_dict[param] = ""
        return param_dict

    @staticmethod
    def __create_random_dict(command: Command) -> dict:
        random_dict = {}
        random_options = command.get_random()
        if random_options is not None:
            for key, value in random_options.items():
                random_dict[key] = random.choice(value)

        return random_dict
