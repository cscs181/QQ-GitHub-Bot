#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 06:23:46
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-07 06:39:13
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any

from src.plugins.github.models import Group

from . import PLATFORMS
from .info import GroupInfo

GROUP_FIELD_MAPPINGS: dict[PLATFORMS, str] = {
    "qq": "qq_group",
    "qqguild": "qqguild_channel",
}


def _get_field_name(info: GroupInfo) -> str:
    if not (field := GROUP_FIELD_MAPPINGS.get(info["type"])):
        raise ValueError(f"Invalid group type {info['type']}")
    return field


async def get_group(info: GroupInfo) -> Group:
    return await Group.get(**{_get_field_name(info): info["group_id"]})


async def create_or_update_group(info: GroupInfo | Group, **data: Any) -> Group:
    if isinstance(info, Group):
        await info.update_from_dict(data).save()
        return info

    group, _ = await Group.update_or_create(
        **{_get_field_name(info): info["group_id"]}, defaults=data
    )
    return group


async def delete_group(info: GroupInfo) -> None:
    group = await get_group(info)
    await group.delete()
