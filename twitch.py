import asyncio
import logging
import pathlib
import signal
from types import FrameType

from chat_bot import ChatBot
from twitch_api import TwitchAPI
from data_types.twitch_bot_config import TwitchBotConfig
from webserver import Webserver

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logging.getLogger("asyncio").disabled = True

log = logging.getLogger(__name__)
signal_to_name = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items())) if v.startswith('SIG') and not v.startswith('SIG_'))


def startup():
    log.info("Reading config")
    config = TwitchBotConfig('secrets.ini')
    TwitchBotConfig.set_config(config)

    base_path = pathlib.Path(__file__).resolve().parent / config['GENERAL']['BASE_FOLDER_NAME']
    TwitchAPI.set_twitch_api(TwitchAPI(config['APP']['CLIENT_ID'], config['APP']['CLIENT_SECRET'], config['USER']['REFRESH_TOKEN'], config['GENERAL']['MONITOR_STREAMS'].split(" "), base_path))
    TwitchAPI.get_twitch_api().setup_event_subs(config['GENERAL']['TWITCH_CALLBACK_URL'], config['GENERAL'].getint('TWITCH_CALLBACK_PORT'))

    log.info("Setting up bot")
    ChatBot.set_bot(ChatBot(config['BOT']['NICK'], config['BOT']['CHAT_OAUTH'], config['APP']['CLIENT_SECRET']))
    # asyncio.ensure_future(_bot.start())
    asyncio.ensure_future(ChatBot.get_bot().start_chat_bot())

    log.info("Setup Webserver")
    Webserver.set_webserver(Webserver())
    asyncio.ensure_future(Webserver.get_webserver().start_webserver(config['WEBSERVER']['BIND_IP'], config['WEBSERVER'].getint('BIND_PORT')))

    log.info("Finished Setup")


def exit_handler(signal_number: int, _: FrameType):
    log.info(f"Exiting ({signal_to_name[signal_number]})")
    if Webserver.get_webserver():
        log.debug("Trying to stop Webserver")
        asyncio.ensure_future(Webserver.get_webserver().stop_webserver())
    if ChatBot.get_bot():
        log.debug("Trying to stop ChatBot")
        asyncio.ensure_future(ChatBot.get_bot().stop_chat_bot())
    if TwitchAPI.get_twitch_api():
        TwitchAPI.get_twitch_api().stop_twitch_api()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    log.info(signal_to_name)
    startup()
    asyncio.get_event_loop().run_forever()