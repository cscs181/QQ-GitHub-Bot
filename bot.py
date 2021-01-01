#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-10 17:12:05
@LastEditors    : yanyongyu
@LastEditTime   : 2021-01-01 17:57:10
@Description    : Entry File of the Bot
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
from nonebot.adapters.ding import Bot as DINGBot

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)
driver.register_adapter("ding", DINGBot)

nonebot.load_plugins("src/plugins")

if __name__ == "__main__":
    nonebot.run(app="bot:app")
