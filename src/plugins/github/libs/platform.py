#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:32:25
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 06:53:11
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Any, Literal, TypedDict, overload

from src.plugins.github.models import User, Group

PLATFORMS = Literal["qq", "qqguild"]

USER_INTEGER_TYPES = Literal["qq"]
USER_STRING_TYPES = Literal["qqguild"]
USER_FIELD_MAPPINGS: dict[PLATFORMS, str] = {"qq": "qq_id", "qqguild": "qqguild_id"}


class UserIntInfo(TypedDict):
    type: USER_INTEGER_TYPES
    user_id: int


class UserStrInfo(TypedDict):
    type: USER_STRING_TYPES
    user_id: str


UserInfo = UserIntInfo | UserStrInfo


GROUP_INTEGER_TYPES = Literal["qq"]
GROUP_STRING_TYPES = Literal["qqguild"]
GROUP_FIELD_MAPPINGS: dict[PLATFORMS, str] = {
    "qq": "qq_group",
    "qqguild": "qqguild_channel",
}


class GroupIntInfo(TypedDict):
    type: GROUP_INTEGER_TYPES
    group_id: int


class GroupStrInfo(TypedDict):
    type: GROUP_STRING_TYPES
    group_id: str


GroupInfo = GroupIntInfo | GroupStrInfo


async def get_user(info: UserInfo) -> User:
    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")
    return await User.get(**{field: info["user_id"]})


async def create_or_update_user(info: UserInfo | User, **data: Any) -> User:
    if isinstance(info, User):
        await info.update_from_dict(data).save()
        return info

    if not (field := USER_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid user type {info['type']}")

    user, _ = await User.update_or_create(**{field: info["user_id"]}, defaults=data)
    return user


async def delete_user(info: UserInfo) -> None:
    user: User = await get_user(info)
    await user.delete()


async def get_group(info: GroupInfo) -> Group:
    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")
    return await Group.get(**{field: info["group_id"]})


async def create_or_update_group(info: GroupInfo | Group, **data: Any) -> Group:
    if isinstance(info, Group):
        await info.update_from_dict(data).save()
        return info

    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")

    group, _ = await Group.update_or_create(**{field: info["group_id"]}, defaults=data)
    return group


async def delete_group(info: GroupInfo) -> None:
    group: Group = await get_group(info)
    await group.delete()
