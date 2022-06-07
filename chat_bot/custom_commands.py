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
            display_commands = stream.commands.keys()
        else:
            log.debug("CustomCommands for all streams loaded")
            for stream in self.Stream.get_streams():
                display_commands.extend(stream.commands.keys())

        for command in display_commands:
            if command not in self.bot.commands.keys() and command not in self.commands:
                self.add_command(commands.Command(command, self.display_command))

    @classmethod
    async def display_command(cls, ctx: commands.Context):
        stream = cls.Stream.get_stream(ctx.channel.name)
        if ctx.command.name in stream.commands.keys() and ctx.command.name not in stream.config['chat-bot'][
            'ignore-commands']:
            if CustomCommands.has_user_right(ctx, stream.commands[ctx.command.name]):
                await ctx.send(stream.commands[ctx.command.name].get_message())


def prepare(bot: ChatBot):
    bot.add_cog(CustomCommands(bot))
