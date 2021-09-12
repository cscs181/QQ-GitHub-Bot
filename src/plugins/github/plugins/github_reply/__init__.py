#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-25 15:20:47
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-26 16:54:53
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.message import event_preprocessor
from nonebot.adapters.cqhttp import MessageEvent

from ... import github_config as config
from ...libs.redis import get_message_info

KEY_GITHUB_REPLY = "github_reply"


async def is_github_reply(bot: Bot, event: Event, state: T_State):
    return KEY_GITHUB_REPLY in state


@event_preprocessor
async def check_reply(bot: Bot, event: Event, state: T_State):
    if not isinstance(event, MessageEvent) or not event.reply:
        return

    message_id = event.reply.message_id
    message_info = get_message_info(str(message_id))
    if message_info:
        # inject reply info into state
        state[KEY_GITHUB_REPLY] = message_info


from . import diff, link, content
