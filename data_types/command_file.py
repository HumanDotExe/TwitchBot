from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import yaml
from schema import Schema, And, Or, Optional, SchemaError

from data_types.types_collection import ValidationException
from utils.string_and_dict_operations import clean_empty

if TYPE_CHECKING:
    from pathlib import Path

log = logging.getLogger(__name__)


class PerStreamConfigError(Exception):
    pass


def create_random_dict():
    random_dict = {}
    for i in range(0, 100):
        random_dict[Optional("random"+str(i))] = And(list)
    return random_dict


def create_param_dict():
    param_dict = {}
    for i in range(0, 100):
        param_dict[Optional("param"+str(i))] = {
                Optional('isRequired', default=False): And(bool),
                Optional('useCallerNameIfEmpty', default=False): And(bool)
        }
    return param_dict


class CommandConfig:
    __schema = Schema(
        {
            'name': And(str),
            Optional('rights', default={'user': True}): {
                Optional('broadcaster', default=False): And(bool),
                Optional('moderator', default=False): And(bool),
                Optional('user', default=True): And(bool)
            },
            'output': {
                Optional('random', default=False): And(bool),
                'message': Or({
                    Optional('online', default=None): Or(str, list, None),
                    Optional('offline', default=None): Or(str, list, None),
                }, str, list),
            },
            Optional('help', default=None): Or(str, None),
            Optional('parameter-count', default=0): And(int),
            Optional("params"): create_param_dict(),
            Optional('random'): create_random_dict()
        }
    )

    @classmethod
    def load_command_file(cls, command_file: Path):
        log.info(f"Reading Command File {command_file.name}")
        with open(command_file, 'r') as file:
            command_config = yaml.safe_load(file)
        return cls.validate(command_config)

    @classmethod
    def validate(cls, command_config: dict):
        try:
            validated = cls.__schema.validate(command_config)
        except SchemaError as e:
            raise ValidationException(f"Command file invalid: {e}")
        if type(validated["output"]["message"]) is str and validated["output"]["random"]:
            raise ValidationException("Message can't be a String if random output is enabled")

        return validated

    @classmethod
    def save_command_file(cls, command_file: Path, command: dict):
        log.info(f"Saving Command {command_file.name}")

        cleaned = clean_empty(command)
        cls.validate(cleaned)

        with open(command_file, 'w') as file:
            yaml.safe_dump(cleaned, file, sort_keys=False)
