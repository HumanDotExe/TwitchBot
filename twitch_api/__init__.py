from __future__ import annotations

import asyncio
import logging
from typing import Optional

from twitchAPI.object.api import TwitchUser
from twitchAPI.twitch import Twitch
from twitchAPI.helper import first

from base.streamer import Streamer
from twitch_api.twitch_user_api import TwitchUserApi

log = logging.getLogger(__name__)


class TwitchAPI:
    __twitch_api: Optional[TwitchAPI] = None
    __per_stream_connections: dict[Streamer, TwitchUserApi] = {}

    @classmethod
    def get_twitch_api(cls) -> TwitchAPI:
        return cls.__twitch_api

    @classmethod
    def set_twitch_api(cls, twitch_api: TwitchAPI):
        cls.__twitch_api = twitch_api

    def __init__(self, client_id: str, client_secret: str, monitored_streams: list[str]):
        self.__client_id = client_id
        self.__client_secret = client_secret

        loop = asyncio.new_event_loop()
        self._twitch: Twitch = loop.run_until_complete(Twitch(client_id, client_secret))

        loop.run_until_complete(self.setup_streamers(monitored_streams))

    async def setup_streamers(self, streams: list[str]):
        for stream in streams:
            user: TwitchUser | None = await first(self._twitch.get_users(logins=[stream]))
            if user is not None:
                streamer = Streamer(user.id, user.login, user.display_name)
                user_api = TwitchUserApi(streamer)
                success = await user_api.authenticate(self.__client_id, self.__client_secret)
                if success:
                    self.__per_stream_connections[streamer] = user_api
                    await user_api.setupEventSub()
                else:
                    log.error(f"Setup failed for streamer {streamer.displayName}")
            else:
                log.warning(f"No user with name {stream} found.")

    async def stop(self):
        log.debug("Stopping global TwitchApi")
        for streamer, per_stream_connection in self.__per_stream_connections.items():
            streamer.config.save()  # save in case of changed nested values
            await per_stream_connection.stop()
        if self._twitch is not None:
            log.debug("Closing Twitch")
            await self._twitch.close()
        log.debug("Global TwitchApi stopped")
