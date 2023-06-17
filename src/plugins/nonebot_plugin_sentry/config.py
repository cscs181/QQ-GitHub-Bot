#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-11-23 18:44:18
@LastEditors    : yanyongyu
@LastEditTime   : 2023-06-17 10:45:33
@Description    : Config for Sentry plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any, Dict, Optional

from nonebot.log import logger
from pydantic import Extra, BaseModel, validator, root_validator


class Config(BaseModel, extra=Extra.allow):
    sentry_dsn: Optional[str]
    sentry_environment: Optional[str] = None

    # https://github.com/getsentry/sentry-python/issues/653
    sentry_default_integrations: bool = False

    @root_validator(pre=True)
    def filter_sentry_configs(cls, values: Dict[str, Any]):
        return {
            key: value for key, value in values.items() if key.startswith("sentry_")
        }

    @validator("sentry_dsn", allow_reuse=True)
    def validate_dsn(cls, v: Optional[str]):
        if not v:
            logger.warning("Sentry DSN not provided! Sentry plugin disabled!")
        return v
