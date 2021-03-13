#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-20 23:59:20
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-13 16:01:37
@Description    : GitHub Main Plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path

import nonebot
from redis import Redis

from .config import Config

# quote with double quotes to use generic typing provided by pylance
redis: "Redis[bytes]" = nonebot.require("redis_provider").redis

# store all github subplugins
_sub_plugins = set()
# load all github plugin config from global config
github_config = Config(**nonebot.get_driver().config.dict())

_sub_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "plugins").resolve()))
