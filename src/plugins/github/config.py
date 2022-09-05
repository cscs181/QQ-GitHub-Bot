#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-21 19:05:28
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-05 09:15:49
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any, Dict

from nonebot.adapters.github.config import GitHubApp
from pydantic import Extra, BaseModel, validator, root_validator


class Config(BaseModel, extra=Extra.ignore):
    github_app: GitHubApp
    github_command_priority: int = 5
    xvfb_installed: bool = False

    @root_validator(pre=True)
    def validate_app(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get("github_app") or not isinstance(
            values["github_apps"][0], GitHubApp
        ):
            raise ValueError(
                "A GitHub App must be provided to use the bot. "
                "See https://github.com/nonebot/adapter-github for more information."
            )
        values.setdefault("github_app", values["github_apps"][0])
        return values

    @validator("github_command_priority")
    def validate_priority(cls, v):
        if v < 1:
            raise ValueError("`github_command_priority` must be greater than 0")
        return v
