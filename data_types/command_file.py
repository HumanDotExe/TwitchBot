from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import yaml
from schema import Schema, And, Or, Optional, SchemaError
from utils.string_and_dict_operations import clean_empty

log = logging.getLogger(__name__)


class PerStreamConfigError(Exception):
    pass


class CommandConfig:
    __schema = Schema(
        {
            'name': And(str),
            Optional('rights', default={'user': True}): {
                Optional('broadcaster', default=False): And(bool),
                Optional('moderator', default=False): And(bool),
                Optional('user', default=True): And(bool)
            },
            'output': Or(str, dict),
            Optional('help', default=None): Or(str, None),
            Optional('parameter-count', default=0): And(int),
            Optional('random'): {
                Optional('random-output', default=False): And(bool),
                Optional('random'+str(range(0, 100))): And(List[str])
            }
        }
    )

    @classmethod
    def load_command_file(cls, command_file: Path):
        log.info(f"Reading Command File {command_file.name}")
        with open(command_file, 'r') as file:
            command_config = yaml.safe_load(file)
        try:
            return cls.__schema.validate(command_config)
        except SchemaError as e:
            log.warning(f"Command file {command_file} invalid, using fallback configuration: {e}")

    @classmethod
    def save_command_file(cls, command_file: Path, command: dict):
        log.info(f"Saving Command {command_file.name}")

        cleaned = clean_empty(command)
        try:
            cls.__schema.validate(cleaned)
        except SchemaError as e:
            log.warning(f"Config invalid, not saving: {e}")
            return

        with open(command_file, 'w') as file:
            yaml.safe_dump(cleaned, file, sort_keys=False)
