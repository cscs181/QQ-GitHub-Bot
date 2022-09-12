import sys
import asyncio
from pathlib import Path
from argparse import ArgumentParser

from aerich import Command

root = Path(__file__).parent.parent

sys.path.append(str(root))

import bot
from src.plugins.tortoise import tortoise_config

cmd = Command(tortoise_config, app="bot", location=str(root / "migrations"))

parser = ArgumentParser()
sub_parser = parser.add_subparsers(required=True)

init = sub_parser.add_parser("init")
init.set_defaults(func=cmd.init)

migrate = sub_parser.add_parser("migrate")
migrate.set_defaults(func=cmd.migrate)

upgrade = sub_parser.add_parser("upgrade")
upgrade.set_defaults(func=cmd.upgrade)

downgrade = sub_parser.add_parser("downgrade")
downgrade.set_defaults(func=cmd.downgrade)


if __name__ == "__main__":
    result = parser.parse_args()
    result = vars(result)
    command = result.pop("func")
    asyncio.run(command())
