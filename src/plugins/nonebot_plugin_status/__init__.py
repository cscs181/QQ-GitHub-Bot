#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2022-01-13 21:01:33
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot import on_notice, get_driver, on_command, on_message

from .config import Config
from .data_source import cpu_status, disk_usage, memory_status, per_cpu_status

global_config = get_driver().config
status_config = Config(**global_config.dict())

command = on_command(
    "状态",
    permission=(status_config.server_status_only_superusers or None) and SUPERUSER,
    priority=10,
)


@command.handle()
async def server_status(matcher: Matcher):
    data = []

    if status_config.server_status_cpu:
        if status_config.server_status_per_cpu:
            data.append("CPU:")
            for index, per_cpu in enumerate(per_cpu_status()):
                data.append(f"  core{index + 1}: {int(per_cpu):02d}%")
        else:
            data.append(f"CPU: {int(cpu_status()):02d}%")

    if status_config.server_status_memory:
        data.append(f"Memory: {int(memory_status()):02d}%")

    if status_config.server_status_disk:
        data.append("Disk:")
        for k, v in disk_usage().items():
            data.append(f"  {k}: {int(v.percent):02d}%")

    await matcher.send(message="\n".join(data))


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
