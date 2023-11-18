import asyncio
import pathlib

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope

from base.twitch_bot_config_v1 import TwitchBotConfig


async def generateRefreshToken():
    config = TwitchBotConfig(pathlib.Path('../secrets.ini'))
    config.read('secrets.ini')

    # setting up Authentication and getting your user id
    twitch = await Twitch(config['APP']['CLIENT_ID'], config['APP']['CLIENT_SECRET'])
    target_scope = [AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.CHANNEL_MODERATE, AuthScope.MODERATOR_READ_FOLLOWERS]
    auth = UserAuthenticator(twitch, target_scope, force_verify=False)
    # this will open your default browser and prompt you with the twitch verification website
    token, refresh_token = await auth.authenticate()

    print(f"token: {token}")
    print(f"refresh_token: {refresh_token}")

if __name__ == "__main__":
    asyncio.new_event_loop().run_until_complete(generateRefreshToken())
