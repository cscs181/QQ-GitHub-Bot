import sys
import asyncio
from pathlib import Path
from functools import partial
from argparse import ArgumentParser

from aerich import Command
from nonebot.log import logger

logger.remove()
root = Path(__file__).parent.parent

sys.path.append(str(root))

import bot
from src.plugins.tortoise import tortoise_config

cmd = Command(tortoise_config, app="bot", location=str(root / "migrations"))

parser = ArgumentParser()
sub_parser = parser.add_subparsers(required=True)

init_db = sub_parser.add_parser("init-db")
init_db.set_defaults(func=partial(cmd.init_db, safe=True))

migrate = sub_parser.add_parser("migrate")
migrate.set_defaults(func=cmd.migrate)

upgrade = sub_parser.add_parser("upgrade")
upgrade.set_defaults(func=cmd.upgrade)

downgrade = sub_parser.add_parser("downgrade")
downgrade.set_defaults(func=cmd.downgrade)

history = sub_parser.add_parser("history")
history.set_defaults(func=cmd.history)

heads = sub_parser.add_parser("heads")
heads.set_defaults(func=cmd.heads)


async def main():
    result = parser.parse_args()
    result = vars(result)
    command = result.pop("func")
    await cmd.init()
    await command()


if __name__ == "__main__":
    asyncio.run(main())
