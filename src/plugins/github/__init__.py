#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-20 23:59:20
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-02 11:29:27
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
github_config = Config.parse_obj(nonebot.get_driver().config)

_sub_plugins |= nonebot.load_plugins(str((Path(__file__).parent / "plugins").resolve()))

from . import apis
