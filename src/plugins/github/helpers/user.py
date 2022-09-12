#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 07:22:30
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-12 09:38:50
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.params import Depends
from tortoise.exceptions import DoesNotExist

from src.plugins.github.models import User
from src.plugins.github.libs.user import get_user

from .event import QQ_EVENT


async def get_qq_user(event: Event) -> User | None:
    if not isinstance(event, QQ_EVENT):
        return
    try:
        return await get_user("qq", event.user_id)
    except DoesNotExist:
        return
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting user: {e}")
        raise


async def get_current_user(qq_user: User | None = Depends(get_qq_user)) -> User | None:
    return qq_user
