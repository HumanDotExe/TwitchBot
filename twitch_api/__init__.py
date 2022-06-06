from __future__ import annotations

import logging
import pathlib
from typing import List

from twitchAPI import Twitch, AuthScope, EventSub, EventSubSubscriptionError, PubSub, TwitchAuthorizationException, \
    TwitchBackendException, TwitchAPIException, PubSubListenTimeoutException, MissingScopeException, \
    refresh_access_token, UserAuthenticator, InvalidRefreshTokenException

from data_types.stream import Stream
from data_types.twitch_bot_config import TwitchBotConfig
from twitch_api.event_sub_callbacks import EventSubCallbacks
from data_types.types_collection import EventSubType, PubSubType
from twitch_api.pubsub_callbacks import PubSubCallbacks

logging.getLogger("twitchAPI.eventsub").disabled = True
logging.getLogger("twitchAPI.twitch").disabled = True
logging.getLogger("urllib3.connectionpool").disabled = True
logging.getLogger("aiohttp.access").disabled = True
logging.getLogger("websockets.client").disabled = True
logging.getLogger("twitchAPI.pubsub").disabled = True

log = logging.getLogger(__name__)


class TwitchAPI:
    __twitch_api = None

    @classmethod
    def set_twitch_api(cls, twitch_api: TwitchAPI):
        cls.__twitch_api = twitch_api

    @classmethod
    def get_twitch_api(cls) -> TwitchAPI:
        return cls.__twitch_api

    @staticmethod
    def user_refresh(token: str, refresh_token: str):
        log.debug("User token refreshed")
        if TwitchBotConfig.get_config() is not None and refresh_token != TwitchBotConfig.get_config()['USER']['REFRESH_TOKEN']:
            log.debug(f"New token: {refresh_token}")
            TwitchBotConfig.get_config()['USER']['REFRESH_TOKEN'] = refresh_token

    def __init__(self, client_id: str, client_secret: str, refresh_token: str, monitored_streams: List[str], base_path: pathlib.Path, user_auth_scope: List[AuthScope] = None, app_auth_scope: List[AuthScope] = None):
        log.debug("Twitch API Object created")
        if user_auth_scope is None:
            user_auth_scope = [AuthScope.CHANNEL_MODERATE]
        if app_auth_scope is None:
            app_auth_scope = [AuthScope.CHANNEL_MODERATE]
        self._client_id = client_id
        self._client_secret = client_secret
        self._monitored_streams = monitored_streams
        self._refresh_token = refresh_token
        self._app_auth_scope = app_auth_scope
        self._user_auth_scope = user_auth_scope
        self._base_path = base_path
        self._twitch: Twitch = None
        self._token = None
        self._event_sub_hook = None
        self._pubsub = None
        self.authenticate()
        self.collect_stream_info()

    def authenticate(self):
        log.info("Authentication started")
        self._twitch = Twitch(self._client_id, self._client_secret)
        self._twitch.user_auth_refresh_callback = self.user_refresh
        log.info("App authentication")
        self._twitch.authenticate_app(self._app_auth_scope)
        log.info("User authentication")
        try:
            self._token, self._refresh_token = refresh_access_token(self._refresh_token, self._client_id, self._client_secret)
        except InvalidRefreshTokenException:
            log.warning(f"Invalid refresh token")
            auth = UserAuthenticator(self._twitch, self._user_auth_scope, force_verify=False)
            self._token, self._refresh_token = auth.authenticate()
            self._twitch.set_user_authentication(self._token, self._user_auth_scope, self._refresh_token)
            TwitchAPI.user_refresh(self._token, self._refresh_token)
            return
        try:
            self._twitch.set_user_authentication(self._token, self._user_auth_scope, self._refresh_token)
            TwitchAPI.user_refresh(self._token, self._refresh_token)
        except MissingScopeException:
            log.warning("Token is missing authentications that are requested")
            auth = UserAuthenticator(self._twitch, self._user_auth_scope, force_verify=False)
            self._token, self._refresh_token = auth.authenticate()
            self._twitch.set_user_authentication(self._token, self._user_auth_scope, self._refresh_token)
            TwitchAPI.user_refresh(self._token, self._refresh_token)

    def collect_stream_info(self):
        log.info("Collecting User Info and Stream Data for monitored streams")
        stream_info = self._twitch.get_streams(user_login=self._monitored_streams)

        from twitch_api.twitch_user_api import TwitchUserAPI
        for info in stream_info['data']:
            stream = Stream(info['user_name'], info['id'], self._base_path)
            stream.stream_started(info['started_at'])
            stream.stream_info_changed(info['title'], info['game_name'], info['is_mature'], info['language'])
            Stream.add_stream(stream)
            TwitchUserAPI.add_twitch_api(TwitchUserAPI(self._client_id, self._client_secret, stream.streamer, None))

        user_info = self._twitch.get_users(logins=self._monitored_streams)
        for info in user_info['data']:
            stream = Stream.get_stream(info['display_name'])
            if stream is None:
                stream = Stream(info['display_name'], info['id'], self._base_path)
                Stream.add_stream(stream)
                TwitchUserAPI.add_twitch_api(TwitchUserAPI(self._client_id, self._client_secret, stream.streamer, None))

    def get_global_chat_emotes(self):
        log.info("Retrieving chat emotes")
        return self._twitch.get_global_emotes()

    def get_global_chat_badges(self):
        log.info("Retrieving Badges")
        return self._twitch.get_global_chat_badges()

    def get_user_id_by_name(self, name: str) -> str:
        log.info(f"Retrieving user id for {name}")
        return self._twitch.get_users(logins=[name])['data'][0]['id']

    def setup_event_subs(self, callback_url: str, callback_port: int):
        log.info("Setting up webhooks")
        self._event_sub_hook = EventSub(callback_url, self._client_id, callback_port, self._twitch)
        self._event_sub_hook.unsubscribe_all()
        self._event_sub_hook.start()

        for stream in Stream.get_streams():
            try:
                stream.set_callback_id(self._event_sub_hook.listen_stream_online(stream.user_id, EventSubCallbacks.on_stream_online), EventSubType.STREAM_ONLINE)
                stream.set_callback_id(self._event_sub_hook.listen_stream_offline(stream.user_id, EventSubCallbacks.on_stream_offline), EventSubType.STREAM_OFFLINE)
                stream.set_callback_id(self._event_sub_hook.listen_channel_update(stream.user_id, EventSubCallbacks.on_channel_update), EventSubType.CHANNEL_UPDATE)
                stream.set_callback_id(self._event_sub_hook.listen_channel_follow(stream.user_id, EventSubCallbacks.on_channel_follow), EventSubType.CHANNEL_FOLLOW)
            except EventSubSubscriptionError:
                log.warning(f"Something went wrong here: No auth for {stream.streamer}.")
            try:
                stream.set_callback_id(self._event_sub_hook.listen_channel_ban(stream.user_id, EventSubCallbacks.on_ban), EventSubType.CHANNEL_BAN)
                stream.set_callback_id(self._event_sub_hook.listen_channel_unban(stream.user_id, EventSubCallbacks.on_unban), EventSubType.CHANNEL_UNBAN)
            except EventSubSubscriptionError:
                log.warning(f"{stream.streamer} does not have the app authorized.")

    def setup_pubsub(self, user_id: str):
        log.info("Setting up PubSub")
        if self._pubsub is None:
            self._pubsub = PubSub(self._twitch)

        self._pubsub.start()
        for stream in Stream.get_streams():
            try:
                stream.set_pubsub_uuid(self._pubsub.listen_chat_moderator_actions(user_id, stream.user_id, PubSubCallbacks.on_chat_moderator_action), PubSubType.CHAT_MODERATOR_ACTIONS)
            except MissingScopeException:
                log.error(f"{stream.streamer} is missing user authentication")
            except TwitchAuthorizationException:
                log.error(f"General authorization problem")
            except TwitchBackendException:
                log.error(f"Twitch servers are down")
            except PubSubListenTimeoutException:
                log.error(f"Ran into timeout")
            except TwitchAPIException:
                log.error(f"Unexpected response")

    def stop_twitch_api(self):
        log.info("Stopping Twitch API")
        if self._event_sub_hook:
            self._event_sub_hook.stop()
            log.debug("EventSub stopped")
        if self._pubsub:
            self._pubsub.stop()
            log.debug("PubSub stopped")
