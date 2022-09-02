#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-10 17:12:05
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-02 10:00:32
@Description    : Entry File of the Bot
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from nonebot.adapters.github import Adapter as GitHubAdapter
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11_Adapter

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(GitHubAdapter)
driver.register_adapter(ONEBOT_V11_Adapter)

config = driver.config
nonebot.load_all_plugins(set(config.plugins), set(config.plugin_dirs))

if __name__ == "__main__":
    nonebot.run(app="__mp_main__:app")
