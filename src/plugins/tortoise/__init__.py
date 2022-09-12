#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 13:43:00
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-12 14:21:11
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from tortoise import Tortoise
from nonebot import get_driver

from src.plugins.github import models

from .config import Config

driver = get_driver()
config = Config.parse_obj(driver.config)

tortoise_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": config.postgres_host,
                "port": config.postgres_port,
                "user": config.postgres_user,
                "password": config.postgres_password,
                "database": config.postgres_db,
            },
        }
    },
    "apps": {"bot": {"models": [models]}},
}


@driver.on_startup
async def init_tortoise():
    await Tortoise.init(config=tortoise_config)


@driver.on_shutdown
async def close_tortoise():
    await Tortoise.close_connections()
