from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from twitchio.ext import commands

from chat_bot.custom_cog import CustomCog

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
    async def uptime(self, ctx: commands.Context, *args):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            command = self.get_command(ctx.command.name, stream)
            if command and self.has_user_right(ctx, command):
                if stream.is_live:
                    message = command.get_message("online")
                else:
                    message = command.get_message("offline")
                await ctx.send(message.format(**self.get_format_dicts(command, ctx, stream, *args)))

    @commands.command(name="game")
    async def game(self, ctx: commands.Context, *args):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            command = self.get_command(ctx.command.name, stream)
            if command and self.has_user_right(ctx, command):
                if stream.is_live:
                    message = command.get_message("online")
                else:
                    message = command.get_message("offline")
                await ctx.send(message.format(**self.get_format_dicts(command, ctx, stream, *args)))

    @commands.command(name="title")
    async def title(self, ctx: commands.Context, *args):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            command = self.get_command(ctx.command.name, stream)
            if command and self.has_user_right(ctx, command):
                if stream.is_live:
                    message = command.get_message("online")
                else:
                    message = command.get_message("offline")
                await ctx.send(message.format(**self.get_format_dicts(command, ctx, stream, *args)))

    @commands.command(name="lurk")
    async def lurk(self, ctx: commands.Context, *args):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            command = self.get_command(ctx.command.name, stream)
            if command and self.has_user_right(ctx, command):
                if stream.is_live:
                    message = command.get_message("online")
                else:
                    message = command.get_message("offline")
                try:
                    message = message.format(**self.get_format_dicts(command, ctx, stream, *args))
                    await ctx.send(message)
                except KeyError as e:
                    log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="unlurk")
    async def unlurk(self, ctx: commands.Context, *args):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            command = self.get_command(ctx.command.name, stream)
            if command and self.has_user_right(ctx, command):
                if stream.is_live:
                    message = command.get_message("online")
                else:
                    message = command.get_message("offline")
                await ctx.send(message.format(**self.get_format_dicts(command, ctx, stream, *args)))


def prepare(bot: ChatBot):
    bot.add_cog(BaseCommands(bot))
