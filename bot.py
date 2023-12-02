#!/usr/bin/env python3
"""
@Author         : yanyongyu
@Date           : 2020-09-10 17:12:05
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-02 15:20:46
@Description    : Entry File of the Bot
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import nonebot
from sqlalchemy.engine.url import URL
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebot.adapters.github import Adapter as GitHubAdapter
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11_Adapter

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(QQAdapter)
driver.register_adapter(GitHubAdapter)
driver.register_adapter(ONEBOT_V11_Adapter)

config = driver.config
config.sqlalchemy_database_url = URL.create(
    "postgresql+asyncpg",
    username=config.postgres_user,
    password=config.postgres_password,
    host=config.postgres_host,
    port=config.postgres_port,
    database=config.postgres_db,
).render_as_string()

nonebot.load_plugins("src/providers")
nonebot.load_all_plugins(set(config.plugins), {"src/plugins"}.union(config.plugin_dirs))

if __name__ == "__main__":
    nonebot.run()
