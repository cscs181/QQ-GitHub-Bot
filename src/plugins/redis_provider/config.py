#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-13 14:45:54
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-13 15:59:09
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional

from pydantic import BaseSettings, validator


class Config(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_username: Optional[str] = None

    class Config:
        extra = "ignore"

    @validator("redis_db", pre=True)
    def replace_empty_str(cls, value):
        return value or 0
