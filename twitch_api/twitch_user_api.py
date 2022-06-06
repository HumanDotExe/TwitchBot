from __future__ import annotations

import logging
from typing import List, Optional

from twitchAPI import AuthScope, Twitch, refresh_access_token, InvalidRefreshTokenException, UserAuthenticator, \
    MissingScopeException

from data_types.stream import Stream

log = logging.getLogger(__name__)


class TwitchUserAPI:
    __user_apis = {}

    @classmethod
    def get_twitch_api(cls, streamer: str) -> Optional[TwitchUserAPI]:
        if streamer.lower() in cls.__user_apis:
            return cls.__user_apis[streamer.lower()]
        return None

    @classmethod
    def add_twitch_api(cls, twitch: TwitchUserAPI):
        cls.__user_apis[twitch._streamer.lower()] = twitch

    def user_refresh(self, token: str, refresh_token: str):
        log.debug("User token refreshed")
        from data_types.stream import Stream
        stream = Stream.get_stream(self._streamer)
        if stream.config is not None and refresh_token != stream.config['chat-bot']['refresh-token']:
            log.debug(f"New User specific token: {refresh_token}")
            stream.config['chat-bot']['refresh-token'] = refresh_token
            stream.save_settings()

    def __init__(self, client_id: str, client_secret: str, streamer: str, user_auth_scope: List[AuthScope] = None):
        log.debug("Twitch User API Object created")
        if user_auth_scope is None:
            user_auth_scope = [AuthScope.CHANNEL_MANAGE_BROADCAST]
        self._client_id = client_id
        self._client_secret = client_secret
        self._streamer = streamer
        self._user_auth_scope = user_auth_scope
        self._twitch: Twitch = None
        self._token = None
        self.authenticate()

    def authenticate(self):
        log.info("User Specific Authentication started")
        self._twitch = Twitch(self._client_id, self._client_secret)
        self._twitch.user_auth_refresh_callback = self.user_refresh
        log.info("User Specific User authentication")
        from data_types.stream import Stream
        refresh_token = Stream.get_stream(self._streamer).config["chat-bot"]["refresh-token"]
        try:
            self._token, refresh_token = refresh_access_token(refresh_token, self._client_id, self._client_secret)
        except InvalidRefreshTokenException:
            log.warning("Invalid refresh token")
            auth = UserAuthenticator(self._twitch, self._user_auth_scope, force_verify=False)
            self._token, refresh_token = auth.authenticate()
            self._twitch.set_user_authentication(self._token, self._user_auth_scope, refresh_token)
            self.user_refresh(self._token, refresh_token)
            return
        try:
            self._twitch.set_user_authentication(self._token, self._user_auth_scope, refresh_token)
            self.user_refresh(self._token, refresh_token)
        except MissingScopeException:
            log.warning("Token is missing authentications that are requested")
            auth = UserAuthenticator(self._twitch, self._user_auth_scope, force_verify=False)
            self._token, refresh_token = auth.authenticate()
            self._twitch.set_user_authentication(self._token, self._user_auth_scope, refresh_token)
            self.user_refresh(self._token, refresh_token)

    def set_title(self, stream: Stream, title: str) -> bool:
        log.info(f"Setting title \"{title}\" for {stream.streamer}")
        return self._twitch.modify_channel_information(broadcaster_id=stream.user_id, title=title)

    def set_game(self, stream: Stream, game: str) -> bool:
        log.info(f"Setting game {game} for {stream.streamer}")
        games = self._twitch.get_games(names=[game])
        if len(games["data"]) is 1:
            return self._twitch.modify_channel_information(broadcaster_id=stream.user_id, game_id=games["data"][0]["id"])
        return False
