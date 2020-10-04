#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-20 23:59:20
@LastEditors    : yanyongyu
@LastEditTime   : 2020-10-04 15:13:26
@Description    : GitHub Main Plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path

import nonebot

from .config import Config

# store all github subplugins
_sub_plugins = set()
# load all github plugin config from global config
github_config = Config(**nonebot.get_driver().config.dict())

_sub_plugins |= nonebot.load_plugins(str(Path(__file__).parent.resolve()))
