#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-10 17:12:05
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-06 21:55:25
@Description    : Entry File of the Bot
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

config = driver.config
nonebot.load_all_plugins(set(config.plugins), set(config.plugin_dirs))

if __name__ == "__main__":
    nonebot.run(app="__mp_main__:app")
