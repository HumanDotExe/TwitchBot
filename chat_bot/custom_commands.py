from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from twitchio.ext import commands

from chat_bot.custom_cog import CustomCog

if TYPE_CHECKING:
    from chat_bot import ChatBot
    from data_types.stream import Stream

log = logging.getLogger(__name__)
logging.getLogger("twitchio.websocket").disabled = True
logging.getLogger("twitchio.client").disabled = True


class CustomCommands(CustomCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.load_custom_commands()

    @commands.Cog.event()
    async def event_ready(self):
        log.info(f'Custom Commands loaded: {self.name}')

    def load_custom_commands(self, stream: Stream = None):
        log.info("Loading custom Commands")
        display_commands = []
        if stream:
            log.debug(f"CustomCommands for {stream.streamer}")
            display_commands = stream.get_custom_commands()
        else:
            log.debug("CustomCommands for all streams loaded")
            for stream in self.Stream.get_streams():
                display_commands.extend(stream.get_custom_commands())

        for command in display_commands:
            if command not in self.bot.commands.keys() and command not in self.commands:
                self.add_command(commands.Command(command, self.display_command))

    @classmethod
    async def display_command(cls, ctx: commands.Context, *args):
        stream = cls.Stream.get_stream(ctx.channel.name)
        command = stream.get_command(ctx.command.name)
        if command and ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            if CustomCommands.has_user_right(ctx, command):
                try:
                    message = command.get_message().format(**cls.get_format_dicts(command, ctx, stream, *args))
                    await ctx.send(message)
                except KeyError as e:
                    log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")


def prepare(bot: ChatBot):
    bot.add_cog(CustomCommands(bot))
