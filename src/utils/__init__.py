#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-12 15:28:17
@LastEditors    : yanyongyu
@LastEditTime   : 2021-09-12 12:22:06
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException
from nonebot.adapters.cqhttp import GroupMessageEvent, PrivateMessageEvent


async def only_private(bot: Bot, event: Event, state: T_State):
    return isinstance(event, PrivateMessageEvent)


async def only_group(bot: Bot, event: Event, state: T_State):
    return isinstance(event, GroupMessageEvent)


async def allow_cancel(bot: Bot, event: Event, state: T_State):
    """An args parser allows to finish the session."""
    message = str(event.get_message())
    if message == "取消":
        await bot.send(event, "已取消")
        raise FinishedException
    state[state["_current_key"]] = str(event.get_message())
