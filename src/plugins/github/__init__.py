"""
@Author         : yanyongyu
@Date           : 2020-09-20 23:59:20
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:43:47
@Description    : GitHub Main Plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from pathlib import Path

import nonebot
from nonebot import get_plugin_config

from .config import Config

# load all github plugin config from global config
config = get_plugin_config(Config)

# load all github subplugins
_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(str((Path(__file__).parent / "plugins").resolve()))

# load all webhook subplugins
_webhook_plugins = set()
_webhook_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "webhooks").resolve())
)

from . import apis as apis
