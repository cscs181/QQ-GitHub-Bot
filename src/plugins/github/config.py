#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-21 19:05:28
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-17 16:00:05
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any, Dict, Literal

from pydantic import Extra, BaseModel, validator, root_validator


class APP(BaseModel):
    app_id: str
    private_key: str
    client_id: str
    client_secret: str

    @validator("private_key", pre=True)
    def concat_key(cls, value: Any) -> Any:
        return "\n".join(value) if isinstance(value, list) else value


class Config(BaseModel, extra=Extra.ignore):
    github_app: APP
    github_theme: Literal["light", "dark"] = "light"
    github_command_priority: int = 5

    @root_validator(pre=True)
    def validate_app(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not (apps := values.get("github_apps")):
            raise ValueError(
                "A GitHub App must be provided to use the bot. "
                "See https://github.com/nonebot/adapter-github for more information."
            )
        values.setdefault("github_app", apps[0])
        return values

    @validator("github_command_priority")
    def validate_priority(cls, v: int):
        if v < 1:
            raise ValueError("`github_command_priority` must be greater than 0")
        return v
