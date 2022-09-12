#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 07:32:17
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-12 09:39:08
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.params import Depends
from tortoise.exceptions import DoesNotExist

from src.plugins.github.models import Group
from src.plugins.github.libs.group import get_group

from .event import QQ_GROUP_MSG_EVENT


async def get_qq_group(event: Event) -> Group | None:
    if not isinstance(event, QQ_GROUP_MSG_EVENT):
        return
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
