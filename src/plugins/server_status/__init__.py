#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2020-09-18 00:46:25
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot import on_command, on_notice

from .data_source import cpu_status, memory_status

command = on_command("状态", permission=SUPERUSER, priority=10)


@command.handle()
async def server_status(bot: Bot, event: Event, state: dict):
    cpu = f"CPU: {cpu_status():02d}%"
    memory = f"Memory: {memory_status():02d}%"
    await bot.send(message=f"{cpu}\n{memory}", event=event)


async def _poke(bot: Bot, event: Event, state: dict) -> bool:
    return (event.detail_type == "notify" and event.sub_type == "poke" and
            event.raw_event["target_id"] == bot.self_id)


poke = on_notice(_poke, priority=10, block=True)
poke.handle()(server_status)
