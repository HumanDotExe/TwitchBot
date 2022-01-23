from __future__ import annotations

import logging
import yaml
from schema import Schema, And, Use, Optional, SchemaError

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
                    Optional('ignore-commands', default=[]): And(list)
                },
            'stream-overlays': {
                'notifications': {
                    'cooldown': And(int),
                    Optional('block', default=[]): And(list),
                    'follow': {
                        'message': And(str),
                        Optional('image', default=None): And(str),
                        Optional('sound', default=None): And(str)
                    },
                    'subscription': {
                        'message': And(str),
                        Optional('image', default=None): And(str),
                        Optional('sound', default=None): And(str)
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
    def load_config(cls, config_file):
        log.info("Reading Config")
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        try:
            validated = cls.__schema.validate(config)
        except SchemaError:
            log.warning(f"Config file {config_file} invalid, using fallback configuration.")
            try:
                config = yaml.safe_load(cls.__fallback)
                validated = cls.__schema.validate(config)
            except SchemaError:
                log.error("Fallback configuration invalid. This should not happen, contact developer.")
                return {}
        return validated

