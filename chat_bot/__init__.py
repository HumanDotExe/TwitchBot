from __future__ import annotations

import logging

from chat_bot.custom_commands import CustomCommands
from chat_bot.mod_commands import ModCommands
from data_types.stream import Stream
from twitchio.ext import commands

log = logging.getLogger(__name__)
logging.getLogger("twitchio.websocket").disabled = True
logging.getLogger("twitchio.client").disabled = True


class ChatBot(commands.Bot):
    __bot = None

    @classmethod
    def set_bot(cls, bot: ChatBot):
        cls.__bot = bot

    @classmethod
    def get_bot(cls) -> ChatBot:
        return cls.__bot

    def __init__(self, username: str, oauth: str, prefix: str = "!"):
        log.debug("Bot Object created")
        streams = Stream.get_streams()
        self._channels = [stream.streamer for stream in streams if stream.config['chat-bot']['save-chatlog']]
        self._prefix = prefix
        self.display_nick = username
        super().__init__(
            token=oauth,
            nick=username,
            prefix=self._prefix,
            initial_channels=self._channels
        )
        self.load_module("chat_bot.base_commands")
        self.load_module("chat_bot.mod_commands")
        self.load_module("chat_bot.custom_commands")

    async def start_chat_bot(self):
        log.info("Starting ChatBot")
        await self.connect()
        log.debug("ChatBot started")

    async def stop_chat_bot(self):
        log.info("Stopping ChatBot")
        await self.close()
        log.debug("ChatBot stopped")

    async def event_ready(self):
        for stream in Stream.get_streams():
            channel = self.get_channel(stream.streamer)
            if channel:
                await channel.send(stream.config['chat-bot']['online-message'])
        log.info(f'{self.display_nick} online!')

    async def event_message(self, message):
        stream = Stream.get_stream(message.channel.name)
        if message.echo:
            if stream.config['stream-overlays']['chat']['include-command-output']:
                chatter = message.channel.get_chatter(self.display_nick)
                badges = ""
                for key, value in chatter.badges.items():
                    if len(badges) == 0:
                        badges += f"{key}/{value}"
                    else:
                        badges += f",{key}/{value}"
                tags = {'badges': badges, 'display-name': chatter.display_name, 'color': chatter.color, 'emotes': ''}
                stream.add_chat_message(message.content, tags)
            stream.write_into_chatlog(self.display_nick, message.content)
            log.debug(f"{message.channel.name} -> {self.display_nick}: {message.content}")
            return
        stream.write_into_chatlog(message.author.display_name, message.content)
        if message.content[0] == self._prefix:
            if stream.config['stream-overlays']['chat']['include-commands']:
                stream.add_chat_message(message.content, message.tags)
        else:
            stream.add_chat_message(message.content, message.tags)
        log.debug(f"{message.channel.name} -> {message.author.display_name}: {message.content}")
        await self.handle_commands(message)
