from __future__ import annotations

import asyncio
import logging
import pathlib
import signal

from typing import TYPE_CHECKING

from beatsaber_request_websocket import BeatSaberIntegration
from chat_bot import ChatBot
from data_types.chat_message import ChatMessage
from data_types.types_collection import ChatBotModuleType
from data_types.twitch_bot_config import TwitchBotConfig
from twitch_api import TwitchAPI
from webserver import Webserver

if TYPE_CHECKING:
    from types import FrameType

debug_file_handler = logging.FileHandler(pathlib.Path(__file__).resolve().parent / "debug" / "debug.log", mode='w')
debug_file_handler.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger("debug-logger").addHandler(debug_file_handler)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logging.getLogger("asyncio").disabled = True
logging.getLogger("debug-logger").propagate = False

log = logging.getLogger(__name__)
signal_to_name = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items())) if v.startswith('SIG') and not v.startswith('SIG_'))


def startup():
    log.info("Reading config")
    config = TwitchBotConfig(pathlib.Path('secrets.ini'))
    TwitchBotConfig.set_config(config)

    beatsaber_exclusive = config.has_section('BEATSABER') and config['BEATSABER'].getboolean("EXCLUSIVE")

    base_path = pathlib.Path(__file__).resolve().parent / config['GENERAL']['BASE_FOLDER_NAME']

    TwitchAPI.set_twitch_api(TwitchAPI(config['APP']['CLIENT_ID'], config['APP']['CLIENT_SECRET'], config['USER']['refresh_token'], config['GENERAL']['MONITOR_STREAMS'].split(" "), base_path))
    if not beatsaber_exclusive:
        TwitchAPI.get_twitch_api().setup_event_subs(config['GENERAL']['TWITCH_CALLBACK_URL'], config['GENERAL'].getint('TWITCH_CALLBACK_PORT'))
        TwitchAPI.get_twitch_api().setup_pubsub(TwitchAPI.get_twitch_api().get_user_id_by_name(config['BOT']['NICK']))
        ChatMessage.set_global_emotes(TwitchAPI.get_twitch_api().get_global_chat_emotes())
        ChatMessage.set_global_badges(TwitchAPI.get_twitch_api().get_global_chat_badges())
    else:
        ChatMessage.set_global_emotes({})
        ChatMessage.set_global_badges({})

    log.info("Setting up bot")
    ChatBot.set_bot(ChatBot(config['BOT']['NICK'], config['BOT']['CHAT_OAUTH']))
    # asyncio.ensure_future(_bot.start())
    asyncio.ensure_future(ChatBot.get_bot().start_chat_bot())

    if not beatsaber_exclusive:
        log.info("Setup Webserver")
        Webserver.set_webserver(Webserver())
        asyncio.ensure_future(Webserver.get_webserver().start_webserver(config['WEBSERVER']['BIND_IP'], config['WEBSERVER'].getint('BIND_PORT')))

    if config.has_section('BEATSABER') and config['BEATSABER'].getboolean("ENABLED"):
        log.info("Setup Beat Saber Integration")
        BeatSaberIntegration.set_beatsaber(BeatSaberIntegration())
        asyncio.ensure_future(BeatSaberIntegration.get_beatsaber().start_beatsaber_integration(config['BEATSABER']['BIND_IP'], config['BEATSABER'].getint('BIND_PORT')))
        if beatsaber_exclusive:
            log.info("Exclusive Beatsaber mode, unloading all modules")
            ChatBot.get_bot().unload_all_modules()
        ChatBot.get_bot().load_module_by_type(ChatBotModuleType.BEATSABER)

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
    if BeatSaberIntegration.get_beatsaber():
        asyncio.ensure_future(BeatSaberIntegration.get_beatsaber().stop_beatsaber_integration())


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    startup()
    asyncio.get_event_loop().run_forever()

