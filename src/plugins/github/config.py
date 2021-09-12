#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-21 19:05:28
@LastEditors    : yanyongyu
@LastEditTime   : 2021-06-03 23:23:48
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional

from nonebot.log import logger
from pydantic import BaseSettings, validator


class Config(BaseSettings):
    github_command_priority: int = 5
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    github_self_host: Optional[str] = None
    github_self_ssl: bool = False
    xvfb_installed: bool = False

    @validator("github_command_priority")
    def validate_priority(cls, v):
        if v < 1:
            raise ValueError("`github_command_priority` must be greater than 0")
        return v

    @validator("github_client_id", "github_client_secret")
    def validate_client(cls, v):
        if not all(v):
            logger.warning(
                "`github_client_id` or `github_client_secret` not provided! "
                "github authorization related plugins are disabled!"
            )
        return v

    @validator("github_self_host")
    def validate_hook(cls, v):
        if not v:
            logger.warning(
                "`github_self_host` not provided! github webhook is disabled!"
            )
        return v

    class Config:
        extra = "ignore"
