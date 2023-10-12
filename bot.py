#!/usr/bin/env python3
"""
@Author         : yanyongyu
@Date           : 2020-09-10 17:12:05
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-11 14:22:23
@Description    : Entry File of the Bot
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebot.adapters.github import Adapter as GitHubAdapter
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11_Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(QQAdapter)
driver.register_adapter(GitHubAdapter)
driver.register_adapter(ONEBOT_V11_Adapter)

config = driver.config
config.sqlalchemy_database_url = (
    "postgresql+asyncpg://"
    f"{config.postgres_user}:{config.postgres_password}@"
    f"{config.postgres_host}:{config.postgres_port}"
    f"/{config.postgres_db}"
)

nonebot.load_plugins("src/providers")
nonebot.load_all_plugins(set(config.plugins), {"src/plugins"}.union(config.plugin_dirs))

if __name__ == "__main__":
    nonebot.run()
