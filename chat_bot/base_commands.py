from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from twitchio.ext import commands

from chat_bot.custom_cog import CustomCog
from data_types.stream import Stream
from utils import timedelta

if TYPE_CHECKING:
    from chat_bot import ChatBot

log = logging.getLogger(__name__)
logging.getLogger("twitchio.websocket").disabled = True
logging.getLogger("twitchio.client").disabled = True


class BaseCommands(CustomCog):
    @commands.Cog.event()
    async def event_ready(self):
        log.info(f'Base Commands loaded: {self.name}')

    @commands.command(name='uptime')
    async def uptime(self, ctx: commands.Context):
        stream = Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            uptime = stream.uptime
            if uptime:
                delta = timedelta.format_timedelta(uptime)
                message = f"{stream.streamer} has been live for {delta['hours']}:{delta['minutes']}h."
            else:
                message = f"{stream.streamer} is not streaming right now."
            await ctx.send(message)

    @commands.command(name="game")
    async def game(self, ctx: commands.Context):
        stream = Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            game = stream.game
            if game:
                message = f"{stream.streamer} is currently playing {game}."
            else:
                message = f"{stream.streamer} is not streaming right now."
            await ctx.send(message)

    @commands.command(name="title")
    async def title(self, ctx: commands.Context):
        stream = Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            title = stream.title
            if title:
                message = f"The stream title is '{title}'."
            else:
                message = f"{stream.streamer} is not streaming right now."
            await ctx.send(message)

    @commands.command(name="lurk")
    async def lurk(self, ctx: commands.Context):
        stream = Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            if stream.is_live:
                message = f"{ctx.author.display_name} has decided to lurk. Have fun!"
            else:
                message = f"There is no stream but {ctx.author.display_name} still decided to lurk. Thank you!"
            await ctx.send(message)

    @commands.command(name="unlurk")
    async def unlurk(self, ctx: commands.Context):
        stream = Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            message = f"{ctx.author.display_name} is trapped in lurking forever. There is no way to unlurk, you are trapped here now!"
            await ctx.send(message)


def prepare(bot: ChatBot):
    bot.add_cog(BaseCommands(bot))
