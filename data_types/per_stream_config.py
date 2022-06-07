from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import yaml
from schema import Schema, And, Or, Optional, SchemaError

from utils.string_and_dict_operations import clean_empty

if TYPE_CHECKING:
    from pathlib import Path

log = logging.getLogger(__name__)


class PerStreamConfigError(Exception):
    pass


class PerStreamConfig:
    __schema = Schema(
        {
            'sync-bans': And(bool),
            'chat-bot':
                {
                    'enabled': And(bool),
                    'save-chatlog': And(bool),
                    Optional('bot-color', default="#FFFFFF"): And(str),
                    'online-message': And(str),
                    Optional('offline-message', default=""): And(str),
                    Optional('ignore-commands', default=[]): And(list),
                    Optional('enable-channel-edit-commands', default=False): And(bool),
                    Optional('refresh-token', default=None): Or(str, None)
                },
            'stream-overlays': {
                'notifications': {
                    'cooldown': And(int),
                    Optional('block', default=[]): And(list),
                    'follow': {
                        'message': And(str),
                        Optional('image', default=None): Or(str, None),
                        Optional('sound', default=None): Or(str, None)
                    },
                    'subscription': {
                        'message': And(str),
                        Optional('image', default=None): Or(str, None),
                        Optional('sound', default=None): Or(str, None)
                    }
                },
                'chat': {
                    'include-commands': And(bool),
                    'include-command-output': And(bool),
                    'message-stays-for': And(int),
                    'message-refresh-rate': And(int),
                    'max-number-of-messages': And(int)
                }
            }
        }
    )

    __fallback = """
    sync-bans: False

    chat-bot:
      enabled: True
      save-chatlog: True
      online-message: "HumanDotExe online!"
      ignore-commands: []
    
    stream-overlays:
      notifications:
        cooldown: 3
        block: []
        follow:
          message: "Thanks for the follow {name}"
        subscription:
          message: "Thanks for the sub {name}"
      chat:
        include-commands: False
        include-command-output: False
        message-stays-for: 60
        message-refresh-rate: 5
        max-number-of-messages: 10
    """

    @classmethod
    def load_config(cls, config_file: Path):
        log.info("Reading Config")
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        try:
            validated = cls.__schema.validate(config)
        except SchemaError as e:
            log.warning(f"Config file {config_file} invalid, using fallback configuration: {e}")
            try:
                config = yaml.safe_load(cls.__fallback)
                validated = cls.__schema.validate(config)
            except SchemaError as e:
                log.error(f"Fallback configuration invalid. This should not happen, contact developer: {e}")
                return {}
        return validated

    @classmethod
    def save_config(cls, config_file: Path, config: dict):
        log.info("Saving Config")

        cleaned = clean_empty(config)
        try:
            cls.__schema.validate(cleaned)
        except SchemaError as e:
            log.warning(f"Config invalid, not saving: {e}")
            return

        with open(config_file, 'w') as file:
            yaml.safe_dump(cleaned, file, sort_keys=False)
