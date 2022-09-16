#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 07:22:30
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-16 05:46:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Event

from src.plugins.github.models import User
from src.plugins.github.libs.platform import get_user

from .event import get_user_info


async def get_current_user(event: Event) -> User | None:
    return await get_user(info) if (info := get_user_info(event)) else None