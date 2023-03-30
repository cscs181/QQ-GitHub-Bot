#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-11-23 18:44:25
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 19:58:06
@Description    : Sentry plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import sentry_sdk
from nonebot import get_driver
from nonebot.log import logger
from sentry_sdk.integrations.logging import EventHandler, BreadcrumbHandler

from .config import Config

driver = get_driver()
global_config = driver.config
config = Config(**global_config.dict())


def init_sentry(config: Config):
    sentry_config = {
        key[7:]: value
        for key, value in config.dict(exclude={"sentry_environment"}).items()
    }
    sentry_sdk.init(
        **sentry_config, environment=config.sentry_environment or driver.env
    )

    logger.add(
        EventHandler("ERROR"),
        filter=lambda r: r["level"].no >= logger.level("ERROR").no,
    )
    logger.add(
        BreadcrumbHandler("INFO"),
        filter=lambda r: r["level"].no >= logger.level("INFO").no,
    )


if config.sentry_dsn:
    init_sentry(config)
