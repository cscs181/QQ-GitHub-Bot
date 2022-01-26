#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-21 00:05:16
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-09 16:43:58
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import inspect
from functools import reduce

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot

from ... import _sub_plugins
from ... import github_config as config

help = on_command("help", priority=config.github_command_priority)
help.__doc__ = """
/help
获取帮助
"""


@help.handle()
async def handle(bot: Bot):
    matchers = reduce(lambda x, y: x.union(y.matcher), _sub_plugins, set())
    docs = "命令列表：\n\n"
    docs += "\n\n".join(
        map(
            lambda x: inspect.cleandoc(x.__doc__),
            filter(lambda x: x.__doc__, matchers),
        )
    )
    await help.finish(docs)
