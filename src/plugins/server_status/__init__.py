#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2020-10-04 16:39:15
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot import get_driver, on_command, on_notice

from .config import Config
from .data_source import cpu_status, memory_status, disk_usage

status_config = Config(**get_driver().config.dict())

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


async def _poke(bot: Bot, event: Event, state: dict) -> bool:
    return (event.detail_type == "notify" and event.sub_type == "poke" and
            str(event.raw_event["target_id"]) == bot.self_id)


poke = on_notice(_poke, priority=10, block=True)
poke.handle()(server_status)
