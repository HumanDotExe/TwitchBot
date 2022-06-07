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


class TestCommands(CustomCog):

    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.event()
    async def event_ready(self):
        log.info(f'Test Commands loaded')

    @commands.command(name="test-command")
    async def test(self, ctx: commands.Context, *args):
        if ctx.author.is_mod:
            out = "Dies ist ein {param1} für {param2}"
            param_dict = {}
            for number in range(1, 3):
                log.debug(number)
                log.debug(args)
                if len(args) > number - 1:
                    param_dict["param" + str(number)] = args[number - 1]
                else:
                    param_dict["param" + str(number)] = ""
            await ctx.send(out.format(**param_dict))


def prepare(bot: ChatBot):
    bot.add_cog(TestCommands(bot))
