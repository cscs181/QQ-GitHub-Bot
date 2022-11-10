#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 06:19:15
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-07 06:32:51
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any

from src.plugins.github.models import User

from . import PLATFORMS
from .info import UserInfo

USER_FIELD_MAPPINGS: dict[PLATFORMS, str] = {"qq": "qq_id", "qqguild": "qqguild_id"}


def _get_field_name(info: UserInfo) -> str:
    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")
    return field


async def get_user(info: UserInfo) -> User:
    return await User.get(**{_get_field_name(info): info["user_id"]})


async def create_or_update_user(info: UserInfo | User, **data: Any) -> User:
    if isinstance(info, User):
        await info.update_from_dict(data).save()
        return info

    user, _ = await User.update_or_create(
        **{_get_field_name(info): info["user_id"]}, defaults=data
    )
    return user


async def delete_user(info: UserInfo) -> None:
    user = await get_user(info)
    await user.delete()
