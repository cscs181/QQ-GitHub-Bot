"""
@Author         : yanyongyu
@Date           : 2020-09-20 23:59:20
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 14:06:14
@Description    : GitHub Main Plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path

import nonebot

from .config import Config

# load all github plugin config from global config
config = Config.parse_obj(nonebot.get_driver().config)

# load all github subplugins
_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(str((Path(__file__).parent / "plugins").resolve()))

# load all webhook subplugins
_webhook_plugins = set()
_webhook_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "webhooks").resolve())
)
