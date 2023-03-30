#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-15 09:00:09
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 20:00:04
@Description    : OneBot v11 matchers for multi pod status plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.rule import to_me
from nonebot import on_type, on_message
from nonebot.adapters.onebot.v11 import PokeNotifyEvent, PrivateMessageEvent

from src.plugins.nonebot_plugin_status.onebot_v11 import _poke
from src.plugins.nonebot_plugin_status import status_permission

from . import server_status

group_poke = on_type(
    (PokeNotifyEvent,),
    rule=to_me(),
    permission=status_permission,
    priority=10,
    block=True,
    handlers=[server_status],
)


poke = on_message(
    _poke,
    permission=status_permission,
    priority=10,
    block=True,
    handlers=[server_status],
)
