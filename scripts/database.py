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

from src.providers.tortoise import tortoise_config

cmd = Command(tortoise_config, app="bot", location=str(root / "migrations"))

parser = ArgumentParser()
sub_parser = parser.add_subparsers(required=True)

init_db = sub_parser.add_parser("init-db")
init_db.set_defaults(func=partial(cmd.init_db, safe=True))


async def _migrate():
    ret = await cmd.migrate()
    if not ret:
        print("No changes detected")
    else:
        print(f"Successfully migrated {ret}")


migrate = sub_parser.add_parser("migrate")
migrate.set_defaults(func=_migrate)


async def _upgrade():
    if migrated := await cmd.upgrade():
        for item in migrated:
            print(f"Successfully upgraded {item}")
    else:
        print("No upgrade items found")


upgrade = sub_parser.add_parser("upgrade")
upgrade.set_defaults(func=_upgrade)


async def _downgrade():
    if files := await cmd.downgrade(-1, False):
        for file in files:
            print(f"Successfully downgraded {file}")


downgrade = sub_parser.add_parser("downgrade")
downgrade.set_defaults(func=_downgrade)


async def _history():
    if versions := await cmd.history():
        for version in versions:
            print(version)
    else:
        print("No history, try migrate first")


history = sub_parser.add_parser("history")
history.set_defaults(func=_history)


async def _heads():
    if head_list := await cmd.heads():
        for head in head_list:
            print(head)
    else:
        print("No available heads, try migrate first")


heads = sub_parser.add_parser("heads")
heads.set_defaults(func=_heads)


async def main():
    result = parser.parse_args()
    result = vars(result)
    command = result.pop("func")
    await cmd.init()
    await command()


if __name__ == "__main__":
    asyncio.run(main())
