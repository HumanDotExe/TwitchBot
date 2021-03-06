from __future__ import annotations

import logging
from configparser import ConfigParser
from typing import TYPE_CHECKING, Optional

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pathlib import Path


class TwitchBotConfigError(Exception):
    pass


class TwitchBotConfig(ConfigParser):
    __config: TwitchBotConfig = None

    @classmethod
    def set_config(cls, config: TwitchBotConfig) -> None:
        cls.__config = config

    @classmethod
    def get_config(cls) -> TwitchBotConfig:
        return cls.__config

    def __init__(self, config_file: Path) -> None:
        log.debug("Config object created")
        super(TwitchBotConfig, self).__init__()
        self.__config_file: Path = config_file
        self.load_config()

    def load_config(self) -> None:
        log.info("Reading Config")
        self.read(self.__config_file)
        self.validate_config()

    def save_config(self) -> None:
        log.info("Saving Config")
        with open(self.__config_file, 'w') as configfile:
            self.write(configfile)

    def set(self, section: str, option: str, value: Optional[str] = None):
        """Overwrite set to save config"""
        super().set(section, option, value)
        self.save_config()

    def add_section(self, section: str):
        """Overwrite add_section to save config"""
        super().add_section(section)
        self.save_config()

    def validate_config(self):
        log.info("Validating Config")
        required_values = {
            'GENERAL': {
                'monitor_streams': None,
                'twitch_callback_url': None,
                'twitch_callback_port': None,
                'base_folder_name': None
            },
            'APP': {
                'client_id': None,
                'client_secret': None
            },
            'BOT': {
                'nick': None,
                'prefix': None,
                'chat_oauth': None
            },
            'WEBSERVER': {
                'bind_ip': None,
                'bind_port': None
            }
        }

        for section, keys in required_values.items():
            if section not in self:
                raise TwitchBotConfigError(
                    'Missing section %s in the config file' % section)

            for key, values in keys.items():
                if key not in self[section] or self[section][key] == '':
                    raise TwitchBotConfigError((
                        'Missing value for %s under section %s in ' +
                        'the config file') % (key, section))

                if values:
                    if self[section][key] not in values:
                        raise TwitchBotConfigError((
                            'Invalid value for %s under section %s in ' +
                            'the config file') % (key, section))
