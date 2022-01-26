#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-12 15:28:17
@LastEditors    : yanyongyu
@LastEditTime   : 2022-01-26 18:16:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import EventMessage
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent


async def only_private(event: PrivateMessageEvent) -> bool:
    return True


async def only_group(event: GroupMessageEvent) -> bool:
    return True


async def allow_cancel(matcher: Matcher, message: Message = EventMessage()):
    """An args parser allows to finish the session."""
    if str(message) == "取消":
        await matcher.finish("已取消")
