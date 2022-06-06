from __future__ import annotations

import logging

from data_types.stream import Stream
from data_types.types_collection import NotificationType

log = logging.getLogger(__name__)


class EventSubCallbacks:

    @staticmethod
    async def on_channel_update(data: dict):
        stream = Stream.get_stream(data['event']['broadcaster_user_name'])
        stream.stream_info_changed(data['event']['title'], data['event']['category_name'], data['event']['is_mature'], data['event']['language'])

    @staticmethod
    async def on_stream_online(data: dict):
        stream = Stream.get_stream(data['event']['broadcaster_user_name'])
        stream.stream_started(data['event']['started_at'])

    @staticmethod
    async def on_stream_offline(data: dict):
        stream = Stream.get_stream(data['event']['broadcaster_user_name'])
        stream.stream_ended()

    @staticmethod
    async def on_channel_follow(data: dict):
        stream = Stream.get_stream(data['event']['broadcaster_user_name'])
        stream.add_to_queue(data['event']['user_name'], NotificationType.FOLLOW)

    @staticmethod
    async def on_ban(data: dict):
        log.debug("Ban callback")
        stream = Stream.get_stream(data['event']['broadcaster_user_name'])
        if data['event']['is_permanent']:
            ban_user = data['event']['user_login']
            reason = f"banned in channel {stream.streamer}"
            if data['event']['reason'] is not "":
                reason = f"{reason}: {data['event']['reason']}"
            from chat_bot import ChatBot
            bot = ChatBot.get_bot()
            for s in Stream.get_streams():
                if stream.streamer is not s.streamer and s.config['sync-bans']:
                    channel = bot.get_channel(s.streamer.lower())
                    if channel and channel.get_chatter(bot.nick).is_mod:
                        log.info(f"Banning {ban_user} in channel {s.streamer} for {reason}")
                        await channel.send(f"/ban {ban_user} {reason}")

    @staticmethod
    async def on_unban(data: dict):
        log.debug("Unban callback")
        stream = Stream.get_stream(data['event']['broadcaster_user_name'])
        unban_user = data['event']['user_login']
        from chat_bot import ChatBot
        bot = ChatBot.get_bot()
        for s in Stream.get_streams():
            if stream.streamer is not s.streamer and s.config['sync-bans']:
                channel = bot.get_channel(s.streamer.lower())
                if channel and channel.get_chatter(bot.nick).is_mod:
                    log.info(f"Unbanning {unban_user} in channel {s.streamer}")
                    await channel.send(f"/unban {unban_user}")

