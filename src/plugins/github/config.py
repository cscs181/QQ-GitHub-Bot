#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-21 19:05:28
@LastEditors    : yanyongyu
@LastEditTime   : 2020-10-04 15:10:41
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pydantic import validator, BaseSettings


class Config(BaseSettings):
    github_command_priority: int = 5

    @validator("github_command_priority")
    def validate_priority(cls, v):
        if v < 1:
            raise ValueError("github_command_priority must be greater than 0")
        return v

    class Config:
        extra = "ignore"
