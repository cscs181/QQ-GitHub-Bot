#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-21 19:05:28
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-16 00:16:27
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional

from pydantic import validator, BaseSettings


class Config(BaseSettings):
    github_command_priority: int = 5
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    github_self_host: Optional[str] = None
    github_self_ssl: bool = False

    @validator("github_command_priority")
    def validate_priority(cls, v):
        if v < 1:
            raise ValueError("`github_command_priority` must be greater than 0")
        return v

    class Config:
        extra = "ignore"
