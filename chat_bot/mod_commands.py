from __future__ import annotations

import logging
from typing import Union, TYPE_CHECKING

from twitchio.ext import commands

from chat_bot.custom_cog import CustomCog
from chat_bot.custom_commands import CustomCommands
from data_types.types_collection import NotificationType

if TYPE_CHECKING:
    from chat_bot import ChatBot

log = logging.getLogger(__name__)
logging.getLogger("twitchio.websocket").disabled = True
logging.getLogger("twitchio.client").disabled = True


class ModCommands(CustomCog):

    @commands.Cog.event()
    async def event_ready(self):
        log.info(f'Mod Commands loaded: {self.name}')

    @commands.command(name="test")
    async def test(self, ctx: commands.Context, notify_type: str = "test", name: str = None):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.command.name not in stream.config['chat-bot']['ignore-commands']:
            if ctx.author.is_mod:
                notification_type = NotificationType.FOLLOW
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
            stream = self.Stream.get_stream(ctx.channel.name)
            stream.load_resources_and_settings()
            cog = self.bot.get_cog("CustomCommands")
            if isinstance(cog, CustomCommands):
                cog.load_custom_commands(stream)
                await ctx.send("Stream settings reloaded!")

    @commands.command(name="ban_queue")
    async def ban_queue(self, ctx: commands.Context, option: str = None, value: Union[str, int] = None):
        if ctx.author.is_mod:
            stream = self.Stream.get_stream(ctx.channel.name)
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
                await ctx.send(
                    "Valid options are 'list' to show queue, 'remove value' to remove 'value' from queue, 'clear' to clear the whole queue and 'ban' to ban everyone in queue.")

    @commands.command(name="disable-cmd")
    async def disable_command(self, ctx: commands.Context, cmd: str):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.author.is_mod and ctx.command.name not in stream.config['chat-bot']['ignore-commands'] or ctx.author.is_broadcaster:
            if cmd.startswith(self.bot.prefix):
                cmd = cmd[len(self.bot.prefix):]
            command = self.bot.get_command(cmd)
            if command is not None:
                if command.name not in stream.config['chat-bot']['ignore-commands']:
                    stream.config['chat-bot']['ignore-commands'].append(command.name)
                    stream.save_settings()
                    await ctx.send(f"command \"{cmd}\" disabled")
                else:
                    await ctx.send(f"command \"{cmd}\" is already disabled")
            else:
                await ctx.send(f"command \"{cmd}\" not found!")

    @commands.command(name="enable-cmd")
    async def enable_command(self, ctx: commands.Context, cmd: str):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.author.is_mod and ctx.command.name not in stream.config['chat-bot']['ignore-commands'] or ctx.author.is_broadcaster:
            if cmd.startswith(self.bot.prefix):
                cmd = cmd[len(self.bot.prefix):]
            command = self.bot.get_command(cmd)
            if command is not None:
                if command.name in stream.config['chat-bot']['ignore-commands']:
                    stream.config['chat-bot']['ignore-commands'].remove(command.name)
                    stream.save_settings()
                    await ctx.send(f"command \"{cmd}\" enabled")
                else:
                    await ctx.send(f"command \"{cmd}\" is already enabled")
            else:
                await ctx.send(f"command \"{cmd}\" not found!")

    @commands.command(name="set-title")
    async def set_title(self, ctx: commands.Context, title: str):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.author.is_mod and ctx.command.name not in stream.config['chat-bot']['ignore-commands'] or ctx.author.is_broadcaster:
            if stream.config["chat-bot"]["enable-channel-edit-commands"] and stream.get_twitch_user_api() is not None:
                if stream.get_twitch_user_api().set_title(stream, title):
                    await ctx.send(f"title set to \"{title}\" by {ctx.author.display_name}")
                else:
                    await ctx.send("could not set title")

    @commands.command(name="set-game")
    async def set_game(self, ctx: commands.Context, game: str):
        stream = self.Stream.get_stream(ctx.channel.name)
        if ctx.author.is_mod and ctx.command.name not in stream.config['chat-bot']['ignore-commands'] or ctx.author.is_broadcaster:
            if stream.config["chat-bot"]["enable-channel-edit-commands"] and stream.get_twitch_user_api() is not None:
                if stream.get_twitch_user_api().set_game(stream, game):
                    await ctx.send(f"game set to \"{game}\" by {ctx.author.display_name}")
                else:
                    await ctx.send("could not set game")


def prepare(bot: ChatBot):
    bot.add_cog(ModCommands(bot))
