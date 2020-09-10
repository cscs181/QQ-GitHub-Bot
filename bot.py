#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-10 17:12:05
@LastEditors    : yanyongyu
@LastEditTime   : 2020-09-10 17:30:10
@Description    : Entry File of the Bot
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot

nonebot.init()
nonebot.load_plugins("src/plugins")

app = nonebot.get_asgi()

if __name__ == "__main__":
    nonebot.run(app="bot:app")
