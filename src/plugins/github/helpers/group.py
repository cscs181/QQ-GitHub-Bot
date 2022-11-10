#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 07:32:17
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-07 06:02:25
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Event
from tortoise.exceptions import DoesNotExist

from src.plugins.github.models import Group
from src.plugins.github.libs.platform import get_group

from .event import get_group_info


async def get_current_group(event: Event) -> Group | None:
    try:
        return await get_group(info) if (info := get_group_info(event)) else None
    except DoesNotExist:
        return None
