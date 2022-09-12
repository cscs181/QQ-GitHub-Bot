#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 07:22:30
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-12 07:31:41
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.log import logger
from nonebot.params import Depends
from tortoise.exceptions import DoesNotExist
from nonebot.adapters.onebot.v11 import MessageEvent

from src.plugins.github.models import User
from src.plugins.github.libs.user import get_user


async def get_qq_user(event: MessageEvent) -> User | None:
    try:
        user = await get_user("qq", event.user_id)
        return user
    except DoesNotExist:
        return
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting user: {e}")
        raise


async def get_current_user(qq_user: User | None = Depends(get_qq_user)) -> User | None:
    return qq_user
