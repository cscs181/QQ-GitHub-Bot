#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-13 14:47:28
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-13 14:53:24
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import redis
import nonebot
from nonebot import get_driver

from .config import Config

global_config = get_driver().config
redis_config = Config(**global_config.dict())

redis_client = redis.Redis(redis_config.redis_host,
                           redis_config.redis_port,
                           redis_config.redis_db,
                           charset="utf-8",
                           password=redis_config.redis_password,
                           username=redis_config.redis_username)

# Export something for other plugin
export = nonebot.export()
export.redis = redis_client
