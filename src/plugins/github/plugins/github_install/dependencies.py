#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-06 12:02:07
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-06 12:02:07
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from tortoise.exceptions import DoesNotExist
from nonebot.adapters.onebot.v11 import MessageEvent

from src.plugins.github.models import User
from src.plugins.github.libs.user import get_user


async def get_qq_user(event: MessageEvent, matcher: Matcher, state: T_State) -> User:
    try:
        user = await get_user("qq", event.user_id)
        state["user"] = user
        return user
    except DoesNotExist:
        await matcher.finish("你还没有绑定 GitHub 帐号，请使用 /install 进行安装")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting user in auth check: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


async def get_current_user(state: T_State) -> User:
    if not (user := state.get("user")):
        raise RuntimeError("Cannot get user from context")
    return user
