#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-11-23 18:44:25
@LastEditors    : yanyongyu
@LastEditTime   : 2021-06-10 23:49:34
@Description    : None
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


class Filter:

    def __init__(self, level="INFO") -> None:
        self.level = level

    def __call__(self, record):
        levelno = logger.level(self.level).no
        return record["level"].no >= levelno


def init(config: Config):
    sentry_config = {
        key[7:]: value
        for key, value in config.dict().items()
        if key != "sentry_environment"
    }
    sentry_sdk.init(**sentry_config,
                    environment=config.sentry_environment or
                    driver.env.environment,
                    default_integrations=False)

    logger.add(EventHandler("ERROR"), filter=Filter("ERROR"))
    logger.add(BreadcrumbHandler("INFO"), filter=Filter("INFO"))


if config.sentry_dsn:
    init(config)
