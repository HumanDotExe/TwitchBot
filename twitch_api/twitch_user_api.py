import logging

from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.oauth import refresh_access_token
from twitchAPI.twitch import Twitch
from twitchAPI.type import MissingScopeException

from base.streamer import Streamer
from twitch_api.eventsub_callbacks import EventSubCallbacks

log = logging.getLogger(__name__)


class TwitchUserApi:
    def user_refresh(self, _: str, refresh_token: str):
        log.debug(f"User token for {self._streamer} refreshed")
        if self._streamer.config.refresh_token != refresh_token:
            self._streamer.config.refresh_token = refresh_token

    def __init__(self, streamer: Streamer):
        log.debug(f"TwitchAPI for streamer {streamer.displayName} created")
        self._streamer: Streamer = streamer
        self._twitch: Twitch | None = None
        self._eventsub: EventSubWebsocket | None = None

    async def authenticate(self, client_id: str, client_secret: str) -> bool:
        log.debug(f"Authenticate TwitchAPI for streamer {self._streamer.displayName}")
        target_scope = self._streamer.config.get_required_auth_scope()
        self._twitch = await Twitch(client_id, client_secret)

        try:
            token, self._streamer.refresh_token = await refresh_access_token(self._streamer.config.refresh_token, client_id, client_secret)
            await self._twitch.set_user_authentication(token, target_scope, self._streamer.config.refresh_token, True)
        except MissingScopeException as e:
            log.error(e)
            return False
        return True

    async def setupEventSub(self):
        eventsub = EventSubWebsocket(self._twitch)
        eventsub.start()
        await eventsub.listen_stream_online(self._streamer.id, EventSubCallbacks.on_stream_online)
        await eventsub.listen_stream_offline(self._streamer.id, EventSubCallbacks.on_stream_offline)
        await eventsub.listen_channel_update_v2(self._streamer.id, EventSubCallbacks.on_channel_update)
        if self._streamer.config.stream_overlays.enabled:
            await eventsub.listen_channel_follow_v2(self._streamer.id, self._streamer.id, EventSubCallbacks.on_channel_follow)

        self._eventsub = eventsub

    async def stop(self):
        log.debug(f"Stopping UserApi for {self._streamer.displayName}")
        if self._eventsub is not None:
            log.debug(f"Stopping EventSub for {self._streamer.displayName}")
            await self._eventsub.stop()
        if self._twitch is not None:
            log.debug(f"Closing Twitch for {self._streamer.displayName}")
            await self._twitch.close()
