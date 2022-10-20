from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from twitchio.ext import commands

from chat_bot.custom_cog import CustomCog

if TYPE_CHECKING:
    from chat_bot import ChatBot
    from data_types.stream import Stream

log = logging.getLogger(__name__)
logging.getLogger("twitchio.websocket").disabled = True
logging.getLogger("twitchio.client").disabled = True


class CustomCommands(CustomCog):

    def __init__(self, bot: ChatBot):
        super().__init__(bot)
        self.load_custom_commands()

    @commands.Cog.event()
    async def event_ready(self):
        log.info(f'Custom Commands loaded: {self.name}')

    def load_custom_commands(self, stream: Optional[Stream] = None):
        log.info("Loading custom Commands")
        display_commands = []
        command_aliases = {}

        if stream:
            log.debug(f"CustomCommands for {stream.streamer}")
            display_commands = stream.get_custom_commands()
            for command_name in display_commands:
                command_aliases[command_name] = self._commands.get(command_name).aliases + stream.get_command(command_name).aliases
        else:
            log.debug("CustomCommands for all streams loaded")
            for stream in self.Stream.get_streams():
                for command_name in stream.get_custom_commands():
                    display_commands.append(command_name)
                    if command_name in command_aliases:
                        command_aliases[command_name].extend(stream.get_command(command_name).aliases)
                    else:
                        command_aliases[command_name] = stream.get_command(command_name).aliases

        for command_name in display_commands:
            if command_name not in self.bot.commands.keys() and command_name not in self.commands:
                bot_command = commands.Command(command_name, self.display_command, aliases=command_aliases[command_name])
                self.add_command(bot_command)

    @classmethod
    async def display_command(cls, ctx: commands.Context, *_, **__):
        stream = cls.Stream.get_stream(ctx.channel.name)
        command = cls.get_command(ctx.command.name, stream)
        if command:
            ctx.kwargs["stream"] = stream
            ctx.kwargs["command"] = command
            try:
                message = command.get_message().format(**cls.get_format_dicts(ctx))
                await ctx.send(message)
            except KeyError as e:
                log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")


def prepare(bot: ChatBot):
    bot.add_cog(CustomCommands(bot))
