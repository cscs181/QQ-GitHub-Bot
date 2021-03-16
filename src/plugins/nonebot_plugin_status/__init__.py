#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-16 17:05:58
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot import get_driver, on_command, on_notice, on_message
from nonebot.adapters.cqhttp import PrivateMessageEvent, PokeNotifyEvent

from .config import Config
from .data_source import cpu_status, per_cpu_status, memory_status, disk_usage

global_config = get_driver().config
status_config = Config(**global_config.dict())

command = on_command("状态", permission=SUPERUSER, priority=10)


@command.handle()
async def server_status(bot: Bot, matcher: Matcher):
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


async def _group_poke(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, PokeNotifyEvent) and str(
        event.user_id) in global_config.superusers


group_poke = on_notice(_group_poke, priority=10, block=True)
group_poke.handle()(server_status)


async def _poke(bot: Bot, event: Event, state: T_State) -> bool:
    return (isinstance(event, PrivateMessageEvent) and
            event.sub_type == "friend" and event.message[0].type == "poke")


poke = on_message(_poke, permission=SUPERUSER, priority=10)
poke.handle()(server_status)
