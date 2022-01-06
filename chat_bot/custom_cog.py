from __future__ import annotations

from twitchio.ext import commands

import chat_bot


class CustomCog(commands.Cog):

    def __init__(self, bot: chat_bot.ChatBot):
        self.bot = bot

    def add_command(self, command: commands.Command):
        self.bot.add_command(command)
        self._commands[command.name] = command

    def remove_command(self, command_name: str):
        self.bot.remove_command(command_name)
        self._commands.pop(command_name)