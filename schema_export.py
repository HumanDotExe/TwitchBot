from data_types.per_stream_config import PerStreamConfig
from data_types.command_file import CommandConfig
import sys
import os
from schema import Schema
import json

if len(sys.argv) != 2:
    print("""\
    This script exports the config file schemas and fallback values to files usable from c#.
    Pass the export target directory as parameter
    
    Usage: schema_export <exportpath>""")
    sys.exit(0)

if not os.path.exists(sys.argv[1]):
    print("""export path does not exist""")
    sys.exit(0)


def dump_schema(schema: Schema, schema_id: str) -> str:
    return json.dumps(schema.json_schema(schema_id), indent=4)


with open(os.path.join(sys.argv[1], "stream_config.json"), "w") as f:
    f.write(dump_schema(PerStreamConfig.get_schema(), "stream_config"))

with open(os.path.join(sys.argv[1], "stream_config_fallback.yaml"), "w") as f:
    f.write(PerStreamConfig.get_fallback())

with open(os.path.join(sys.argv[1], "command_file.json"), "w") as f:
    f.write(dump_schema(CommandConfig.get_schema(), "command_file"))

print("files exported")
