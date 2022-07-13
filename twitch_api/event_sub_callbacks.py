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
            for s in Stream.get_streams():
                if stream.streamer != s.streamer and s.config['sync-bans']:
                    from twitch_api import TwitchAPI
                    if TwitchAPI.get_twitch_api().ban_user(stream.user_id, data['event']['user_id'], reason):
                        log.info(f"Banning {ban_user} in channel {s.streamer} for {reason}")
                    else:
                        log.warning(f"Banning {ban_user} in channel {s.streamer} for {reason} failed. Check the permissions.")

    @staticmethod
    async def on_unban(data: dict):
        log.debug("Unban callback")
        stream = Stream.get_stream(data['event']['broadcaster_user_name'])
        unban_user = data['event']['user_login']
        for s in Stream.get_streams():
            if stream.streamer != s.streamer and s.config['sync-bans']:
                from twitch_api import TwitchAPI
                if TwitchAPI.get_twitch_api().unban_user(stream.user_id, data['event']['user_id']):
                    log.info(f"Unbanning {unban_user} in channel {s.streamer}")
                else:
                    log.warning(f"Unbanning {unban_user} in channel {s.streamer} failed. Check the permissions.")

