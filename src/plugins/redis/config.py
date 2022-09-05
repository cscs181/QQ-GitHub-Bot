#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-13 14:45:54
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-05 08:17:41
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pydantic import Extra, BaseSettings, validator


class Config(BaseSettings, extra=Extra.ignore):
    redis_host: str
    redis_port: int
    redis_db: int = 0
    redis_password: str | None = None
    redis_username: str | None = None

    @validator("redis_db", pre=True)
    def replace_empty_str(cls, value):
        return value or 0
