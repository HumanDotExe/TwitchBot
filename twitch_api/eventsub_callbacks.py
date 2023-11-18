import logging

from twitchAPI.object.eventsub import ChannelFollowEvent, StreamOnlineEvent, StreamOfflineEvent, ChannelUpdateEvent

log = logging.getLogger(__name__)


class EventSubCallbacks:
    @staticmethod
    async def on_channel_update(data: ChannelUpdateEvent):
        log.info(f"on_channel_update callback called: data: {data}")

    @staticmethod
    async def on_stream_online(data: StreamOnlineEvent):
        log.info(f"on_stream_online callback called: data: {data}")

    @staticmethod
    async def on_stream_offline(data: StreamOfflineEvent):
        log.info(f"on_stream_offline callback called: data: {data}")

    @staticmethod
    async def on_channel_follow(data: ChannelFollowEvent):
        log.info(f"on_channel_follow callback called: data: {data}")
