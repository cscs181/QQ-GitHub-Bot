#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-21 00:05:16
@LastEditors    : yanyongyu
@LastEditTime   : 2020-09-21 01:10:50
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"
__package__ = "github.github_help"

import inspect
from functools import reduce

from nonebot import on_command
from nonebot.typing import Bot, Event

from .. import _sub_plugins

help = on_command("help", priority=5)
help.__doc__ = """
/help
获取帮助
"""


@help.handle()
async def handle(bot: Bot, event: Event, state: dict):
    matchers = reduce(lambda x, y: x.union(y.matcher), _sub_plugins, set())
    docs = "命令列表：\n"
    docs += "\n".join(
        map(lambda x: inspect.cleandoc(x.__doc__),
            filter(lambda x: x.__doc__, matchers)))
    await help.finish(docs)
