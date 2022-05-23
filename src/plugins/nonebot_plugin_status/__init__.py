#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2022-05-23 05:41:46
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from jinja2 import Environment
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot import on_notice, get_driver, on_command, on_message

from .config import Config
from .data_source import uptime, cpu_status, disk_usage, memory_status, per_cpu_status

global_config = get_driver().config
status_config = Config(**global_config.dict())

_ev = Environment(autoescape=False, enable_async=True)
_t = _ev.from_string(status_config.server_status_template)

command = on_command(
    "状态",
    permission=(status_config.server_status_only_superusers or None) and SUPERUSER,
    priority=10,
)


@command.handle()
async def server_status(matcher: Matcher):
    message = await _t.render_async(
        cpu_usage=cpu_status(),
        per_cpu_usage=per_cpu_status(),
        memory_usage=memory_status(),
        disk_usage=disk_usage(),
        uptime=uptime(),
    )
    await matcher.send(message=message.strip("\n"))


try:
    from nonebot.adapters.onebot.v11 import PokeNotifyEvent, PrivateMessageEvent
except ImportError:
    pass
else:

    async def _group_poke(event: PokeNotifyEvent) -> bool:
        return event.is_tome() and (
            not status_config.server_status_only_superusers
            or str(event.user_id) in global_config.superusers
        )

    group_poke = on_notice(_group_poke, priority=10, block=True)
    group_poke.handle()(server_status)

    async def _poke(event: PrivateMessageEvent) -> bool:
        return event.sub_type == "friend" and event.message[0].type == "poke"

    poke = on_message(
        _poke,
        permission=(status_config.server_status_only_superusers or None) and SUPERUSER,
        priority=10,
    )
    poke.handle()(server_status)
