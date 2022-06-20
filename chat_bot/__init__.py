from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from twitchio.ext import commands

from data_types.types_collection import ChatBotModuleType

if TYPE_CHECKING:
    from twitchio import Channel, Message

log = logging.getLogger(__name__)
logging.getLogger("twitchio.websocket").disabled = True
logging.getLogger("twitchio.client").disabled = True


class ChatBot(commands.Bot):
    from data_types.stream import Stream
    __bot = None

    @classmethod
    def set_bot(cls, bot: ChatBot):
        cls.__bot = bot

    @classmethod
    def get_bot(cls) -> ChatBot:
        return cls.__bot

    def __init__(self, username: str, oauth: str, prefix: str = "!"):
        log.debug("Bot Object created")
        # the .lower() is needed in twitchio 2.2.0 because of a bug that does not call event_ready if there
        # are uppercase characters in the channel list
        self._channels = [stream.streamer.lower() for stream in self.Stream.get_streams() if
                          stream.config['chat-bot']['enabled']]
        self._prefix = prefix
        self.display_nick = username
        self._bot_tags = {}
        super().__init__(
            token=oauth,
            nick=username,
            prefix=self._prefix,
            initial_channels=self._channels
        )

        from chat_bot.custom_cog import CustomCog
        CustomCog.load_global_commands()

        self.load_module_by_type(ChatBotModuleType.BASE)
        self.load_module_by_type(ChatBotModuleType.MOD)
        self.load_module_by_type(ChatBotModuleType.CUSTOM)
        self.load_module("chat_bot.test_commands")

    def load_module_by_type(self, module_type: ChatBotModuleType):
        if module_type in ChatBotModuleType and module_type.value not in self._modules:
            self.load_module(module_type.value)

    def unload_module_by_type(self, module_type: ChatBotModuleType):
        if module_type in ChatBotModuleType and module_type.value not in self._modules:
            self.unload_module(module_type.value)

    def reload_module_by_type(self, module_type: ChatBotModuleType):
        if module_type in ChatBotModuleType and module_type.value not in self._modules:
            self.reload_module(module_type.value)

    def unload_all_modules(self):
        for module_type in ChatBotModuleType:
            self.unload_module_by_type(module_type)

    async def start_chat_bot(self):
        log.info("Starting ChatBot")
        await self.connect()
        log.debug("ChatBot started")

    async def send_chat_message_on_stop(self):
        for channel in self.connected_channels:
            stream = self.Stream.get_stream(channel.name)
            offline_message = stream.config['chat-bot']['offline-message'].format(bot_name=self.display_nick)
            if len(offline_message) > 0:
                await channel.send(offline_message)

    async def stop_chat_bot(self):
        log.info("Stopping ChatBot")
        await self.send_chat_message_on_stop()
        await self.close()
        log.debug("ChatBot stopped")

    async def event_ready(self):
        for stream in self.Stream.get_streams():
            channel = self.get_channel(stream.streamer)
            if channel:
                await channel.send(stream.config['chat-bot']['online-message'].format(bot_name=self.display_nick))
        log.info(f'{self.display_nick} online!')

    async def create_bot_tag_for_channel(self, channel: Channel):
        chatter = channel.get_chatter(self.display_nick)
        if chatter is not None:
            badges = ""
            for key, value in chatter.badges.items():
                if len(badges) == 0:
                    badges += f"{key}/{value}"
                else:
                    badges += f",{key}/{value}"
            self._bot_tags[channel.name] = {'badges': badges, 'display-name': chatter.display_name, 'emotes': ''}

    async def get_bot_tags_for_channel(self, channel: Channel) -> dict:
        if channel.name not in self._bot_tags:
            await self.create_bot_tag_for_channel(channel)
        return self._bot_tags[channel.name]

    async def event_message(self, message: Message):
        stream = self.Stream.get_stream(message.channel.name)
        if message.echo:
            stream.add_chat_message(message.content, await self.get_bot_tags_for_channel(message.channel), True)
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

    async def send(self, message: str, channel_name: str):
        channel = self.get_channel(channel_name)
        if channel:
            await channel.send(message)

    async def announce(self, message: str, channel_name: str):
        channel = self.get_channel(channel_name)
        if channel:
            await channel.send("/announce " + message)

    @property
    def prefix(self):
        return self._prefix
