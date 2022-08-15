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
    async def uptime(self, ctx: commands.Context, *_, **__):
        command = ctx.kwargs["command"]
        if ctx.kwargs["stream"].is_live:
            message = command.get_message("online")
        else:
            message = command.get_message("offline")
        try:
            message = message.format(**self.get_format_dicts(ctx))
            await ctx.send(message)
        except KeyError as e:
            log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="game")
    async def game(self, ctx: commands.Context, *_, **__):
        command = ctx.kwargs["command"]
        if ctx.kwargs["stream"].is_live:
            message = command.get_message("online")
        else:
            message = command.get_message("offline")
        try:
            message = message.format(**self.get_format_dicts(ctx))
            await ctx.send(message)
        except KeyError as e:
            log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="title")
    async def title(self, ctx: commands.Context, *_, **__):
        command = ctx.kwargs["command"]
        if ctx.kwargs["stream"].is_live:
            message = command.get_message("online")
        else:
            message = command.get_message("offline")
        try:
            message = message.format(**self.get_format_dicts(ctx))
            await ctx.send(message)
        except KeyError as e:
            log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="lurk")
    async def lurk(self, ctx: commands.Context, *_, **__):
        command = ctx.kwargs["command"]
        if ctx.kwargs["stream"].is_live:
            message = command.get_message("online")
        else:
            message = command.get_message("offline")
        try:
            message = message.format(**self.get_format_dicts(ctx))
            await ctx.send(message)
        except KeyError as e:
            log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="unlurk")
    async def unlurk(self, ctx: commands.Context, *_, **__):
        command = ctx.kwargs["command"]
        if ctx.kwargs["stream"].is_live:
            message = command.get_message("online")
        else:
            message = command.get_message("offline")
        try:
            message = message.format(**self.get_format_dicts(ctx))
            await ctx.send(message)
        except KeyError as e:
            log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")


def prepare(bot: ChatBot):
    bot.add_cog(BaseCommands(bot))
