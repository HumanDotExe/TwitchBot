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

    @commands.command(name="add_alert")
    async def add_alert(self, ctx: commands.Context, notify_type: str = "follow", name: str = None, *_, **__):
        command = ctx.kwargs["command"]
        if name is None:
            name = "TestUser"
        if notify_type in NotificationType.SUB.value:
            notification_type = NotificationType.SUB
        elif notify_type in NotificationType.FOLLOW.value:
            notification_type = NotificationType.FOLLOW
        else:
            return
        ctx.kwargs["stream"].add_to_queue(name, notification_type)
        try:
            message = command.get_message().format(**self.get_format_dicts(ctx))
            await ctx.send(message)
        except KeyError as e:
            log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="reload")
    async def reload(self, ctx: commands.Context):
        command = ctx.kwargs["command"]
        ctx.kwargs["stream"].load_resources_and_settings()
        cog = self.bot.get_cog("CustomCommands")
        if isinstance(cog, CustomCommands):
            cog.load_custom_commands(ctx.kwargs["stream"])
            try:
                message = command.get_message().format(**self.get_format_dicts(ctx))
                await ctx.send(message)
            except KeyError as e:
                log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    # @commands.command(name="ban_queue")
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

    @commands.command(name="disable_command")
    async def disable_command(self, ctx: commands.Context, cmd: str, *_, **__):
        command = ctx.kwargs["command"]
        stream = ctx.kwargs["stream"]
        if cmd.startswith(self.bot.prefix):
            cmd = cmd[len(self.bot.prefix):]
        target_command = self.get_command(cmd, stream)
        if target_command is not None:
            if cmd not in stream.config['chat-bot']['ignore-commands']:
                stream.config['chat-bot']['ignore-commands'].append(cmd)
                stream.save_settings()
                message = command.get_message("success")
            else:
                message = command.get_message("fail")
        else:
            message = command.get_message("not_found")
        try:
            message = message.format(**self.get_format_dicts(ctx))
            await ctx.send(message)
        except KeyError as e:
            log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="enable_command")
    async def enable_command(self, ctx: commands.Context, cmd: str, *_, **__):
        command = ctx.kwargs["command"]
        stream = ctx.kwargs["stream"]
        if cmd.startswith(self.bot.prefix):
            cmd = cmd[len(self.bot.prefix):]
        target_command = self.get_command(cmd, stream)
        if target_command:
            if cmd in stream.config['chat-bot']['ignore-commands']:
                stream.config['chat-bot']['ignore-commands'].remove(cmd)
                stream.save_settings()
                message = command.get_message("success")
            else:
                message = command.get_message("fail")
        else:
            message = command.get_message("not_found")
        try:
            message = message.format(**self.get_format_dicts(ctx))
            await ctx.send(message)
        except KeyError as e:
            log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="set_title")
    async def set_title(self, ctx: commands.Context, title: str, *_, **__):
        command = ctx.kwargs["command"]
        stream = ctx.kwargs["stream"]
        if stream.config["chat-bot"]["enable-channel-edit-commands"] and stream.get_twitch_user_api() is not None:
            if stream.get_twitch_user_api().set_title(stream, title):
                message = command.get_message("success")
            else:
                message = command.get_message("fail")
            try:
                message = message.format(**self.get_format_dicts(ctx))
                await ctx.send(message)
            except KeyError as e:
                log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")

    @commands.command(name="set_game")
    async def set_game(self, ctx: commands.Context, game: str, *_, **__):
        command = ctx.kwargs["command"]
        stream = ctx.kwargs["stream"]
        if stream.config["chat-bot"]["enable-channel-edit-commands"] and stream.get_twitch_user_api() is not None:
            if stream.get_twitch_user_api().set_game(stream, game):
                message = command.get_message("success")
            else:
                message = command.get_message("fail")
            try:
                message = message.format(**self.get_format_dicts(ctx))
                await ctx.send(message)
            except KeyError as e:
                log.warning(f"Key {e} was not defined in {command.name}.cmd file. Please correct.")


def prepare(bot: ChatBot):
    bot.add_cog(ModCommands(bot))
