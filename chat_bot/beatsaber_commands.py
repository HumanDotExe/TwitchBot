from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from twitchio.ext import commands

from chat_bot.custom_cog import CustomCog

if TYPE_CHECKING:
    from chat_bot import ChatBot
    from twitchio import Message

log = logging.getLogger(__name__)
logging.getLogger("twitchio.websocket").disabled = True
logging.getLogger("twitchio.client").disabled = True


class BeatSaberCommands(CustomCog):

    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.event()
    async def event_ready(self):
        log.info(f'Beat Saber Commands loaded: {self.name}')

    @commands.command(name="bsr", aliases=["queue", "remove", "detail"])
    async def beat_saber_normal_command(self, ctx: commands.Context):
        stream = self.Stream.get_stream(ctx.channel.name)
        if stream.beatsaber_websocket is not None:
            await stream.beatsaber_websocket.send_json(self.message_to_json(ctx.message))
            log.debug(self.message_to_json(ctx.message))

    @commands.command(name="open", aliases=["close"])
    async def beat_saber_mod_command(self, ctx: commands.Context):
        if ctx.author.is_mod:
            stream = self.Stream.get_stream(ctx.channel.name)
            if stream.beatsaber_websocket is not None:
                await stream.beatsaber_websocket.send_json(self.message_to_json(ctx.message))
                log.debug(self.message_to_json(ctx.message))

    @classmethod
    def message_to_json(cls, message: Message):
        json_message = {
            "Id": message.id,
            "UserName": message.author.name,
            "DisplayName": message.author.display_name,
            "Color": message.author.color,
            "IsModerator": message.author.is_mod,
            "IsBroadcaster": message.author.is_broadcaster,
            "IsSubscriber": message.author.is_subscriber,
            "IsTurbo": False,
            "IsVip": False,
            "Badges": [],
            "Message": message.content,
            "Command": "c"
        }
        return json.loads(json.dumps(json_message))


def prepare(bot: ChatBot):
    bot.add_cog(BeatSaberCommands(bot))
