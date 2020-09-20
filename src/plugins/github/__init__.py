#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-20 23:59:20
@LastEditors    : yanyongyu
@LastEditTime   : 2020-09-21 00:53:44
@Description    : GitHub Main Plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path

import nonebot

_sub_plugins = set()

# !all matcher in github plugin using priority 5
# TODO: Set priority in config file
_sub_plugins |= nonebot.load_plugins(str(Path(__file__).parent.resolve()))
