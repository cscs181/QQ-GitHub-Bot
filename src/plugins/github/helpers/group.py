#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 07:32:17
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-12 07:33:22
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.log import logger
from nonebot.params import Depends
from tortoise.exceptions import DoesNotExist
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from src.plugins.github.models import Group
from src.plugins.github.libs.group import get_group


async def get_qq_group(event: GroupMessageEvent) -> Group | None:
    try:
        return await get_group("qq", event.group_id)
    except DoesNotExist:
        return
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting group: {e}")
        raise


async def get_current_group(
    qq_group: Group | None = Depends(get_qq_group),
) -> Group | None:
    return qq_group
