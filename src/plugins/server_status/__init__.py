#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2020-10-07 01:10:33
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot import get_driver, on_command, on_notice, on_message

from .config import Config
from .data_source import cpu_status, memory_status, disk_usage

global_config = get_driver().config
status_config = Config(**global_config.dict())

command = on_command("状态", permission=SUPERUSER, priority=10)


@command.handle()
async def server_status(bot: Bot, event: Event, state: dict):
    data = []

    if status_config.server_status_cpu:
        data.append(f"CPU: {int(cpu_status()):02d}%")

    if status_config.server_status_memory:
        data.append(f"Memory: {int(memory_status()):02d}%")

    if status_config.server_status_disk:
        data.append(f"Disk:\n" + "\n".join(
            f"  {k}: {int(v.percent):02d}%" for k, v in disk_usage().items()))

    await bot.send(message="\n".join(data), event=event)


async def _group_poke(bot: Bot, event: Event, state: dict) -> bool:
    return (event.detail_type == "notify" and event.sub_type == "poke" and
            str(event.raw_event["target_id"]) == bot.self_id and
            event.user_id in global_config.superusers)


group_poke = on_notice(_group_poke, priority=10, block=True)
group_poke.handle()(server_status)


async def _poke(bot: Bot, event: Event, state: dict) -> bool:
    return (event.detail_type == "private" and event.sub_type == "friend" and
            event.message[0].type == "poke")


poke = on_message(_poke, permission=SUPERUSER, priority=10)
poke.handle()(server_status)
