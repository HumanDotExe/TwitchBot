from __future__ import annotations

import asyncio
import logging
import pathlib
import signal
from typing import TYPE_CHECKING

from base.paths import Paths
from base.twitch_bot_config_v1 import TwitchBotConfig
from twitch_api import TwitchAPI

if TYPE_CHECKING:
    from types import FrameType

debug_path = pathlib.Path(__file__).resolve().parent / "debug"
debug_path.mkdir(exist_ok=True)
debug_file_handler = logging.FileHandler(debug_path / "debug.log", mode='w')
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

    Paths.base_path = pathlib.Path(__file__).resolve().parent / config['GENERAL']['BASE_FOLDER_NAME']

    twitch_api = TwitchAPI(config['APP']['CLIENT_ID'], config['APP']['CLIENT_SECRET'], config['GENERAL']['MONITOR_STREAMS'].split(" "))
    TwitchAPI.set_twitch_api(twitch_api)


async def exit_handler(signal_number: int, _: FrameType, event_loop: asyncio.events = None):
    log.info(f"Exiting ({signal_to_name[signal_number]})")
    if TwitchAPI.get_twitch_api() is not None:
        await TwitchAPI.get_twitch_api().stop()

    if event_loop is not None and event_loop.is_running() and not event_loop.is_closed():
        log.debug("Shutting down loop")
        event_loop.stop()


if __name__ == "__main__":
    startup()
    log.info("Startup finished, bot is running")
    loop = asyncio.new_event_loop()
    signal.signal(signal.SIGINT, lambda x, y: asyncio.ensure_future(exit_handler(x, y, loop)))
    signal.signal(signal.SIGTERM, lambda x, y: asyncio.ensure_future(exit_handler(x, y, loop)))
    loop.run_forever()

