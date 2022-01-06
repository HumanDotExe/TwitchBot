from __future__ import annotations

import logging
from typing import Union

from twitchio.ext import commands

import chat_bot
from chat_bot.custom_cog import CustomCog
from data_types.stream import Stream
from data_types.types_collection import NotificationType

log = logging.getLogger(__name__)
logging.getLogger("twitchio.websocket").disabled = True
logging.getLogger("twitchio.client").disabled = True


class ModCommands(CustomCog):

    @commands.Cog.event()
    async def event_ready(self):
        log.info(f'Mod Commands loaded: {self.name}')

    @commands.command(name="test")
    async def test(self, ctx: commands.Context, notify_type: str = "test", name: str = None):
        stream = Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.ignore_commands:
            if ctx.author.is_mod:
                notification_type = NotificationType.TEST
                if name is None:
                    name = "TestUser"
                if notify_type in NotificationType.SUB.value:
                    notification_type = NotificationType.SUB
                elif notify_type in NotificationType.FOLLOW.value:
                    notification_type = NotificationType.FOLLOW
                stream.add_to_queue(name, notification_type)
                await ctx.send(f"Test added to {notification_type.name}-queue")
            else:
                await ctx.send("You don't have permission to do this!")

    @commands.command(name="reload")
    async def reload(self, ctx: commands.Context):
        if ctx.author.is_mod:
            stream = Stream.get_stream(ctx.channel.name)
            stream.load_resources_and_settings()
            cog = self.bot.get_cog("CustomCommands")
            cog.load_custom_commands(stream)
            await ctx.send("Stream settings reloaded!")

    @commands.command(name="ban_queue")
    async def ban_queue(self, ctx: commands.Context, option: str = None, value: Union[str, int] = None):
        if ctx.author.is_mod:
            stream = Stream.get_stream(ctx.channel.name)
            if option == "list":
                counter = 0
                message = "Ban Queue:              "
                for entry in stream.ban_queue:
                    message += f"{counter} - {entry}"
                    counter += 1
                await ctx.send(message)
            elif option == "remove":
                if value is not None:
                    if type(value) is int and len(stream.ban_queue) >= value:
                        stream.ban_queue.pop(value)
                    elif type(value) is str and value in stream.ban_queue:
                        stream.ban_queue.remove(value)
            elif option == "clear":
                stream.ban_queue = []
            elif option == "ban":
                for entry in stream.ban_queue:
                    await ctx.send(f"/ban {entry}")
            else:
                await ctx.send("Valid options are 'list' to show queue, 'remove value' to remove 'value' from queue, 'clear' to clear the whole queue and 'ban' to ban everyone in queue.")


def prepare(bot: chat_bot.ChatBot):
    bot.add_cog(ModCommands(bot))
