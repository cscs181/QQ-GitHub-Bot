#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-21 19:05:28
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-02 11:28:43
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pydantic import Extra, BaseModel, validator


class Config(BaseModel, extra=Extra.ignore):
    github_command_priority: int = 5
    xvfb_installed: bool = False

    @validator("github_command_priority")
    def validate_priority(cls, v):
        if v < 1:
            raise ValueError("`github_command_priority` must be greater than 0")
        return v
