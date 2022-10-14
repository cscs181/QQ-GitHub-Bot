#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-14 17:05:22
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import contextlib

from jinja2 import Environment
from nonebot import get_driver
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER

from .config import Config
from .data_source import uptime, cpu_status, disk_usage, memory_status, per_cpu_status

global_config = get_driver().config
status_config = Config.parse_obj(global_config)
status_permission = (status_config.server_status_only_superusers or None) and SUPERUSER

_ev = Environment(autoescape=False, enable_async=True)
_t = _ev.from_string(status_config.server_status_template)


async def server_status(matcher: Matcher):
    message = await _t.render_async(
        cpu_usage=cpu_status(),
        per_cpu_usage=per_cpu_status(),
        memory_usage=memory_status(),
        disk_usage=disk_usage(),
        uptime=uptime(),
    )
    await matcher.send(message=message.strip("\n"))


if status_config.server_status_enabled:
    from .common import command

    with contextlib.suppress(ImportError):
        import nonebot.adapters.onebot.v11

        from .onebot_v11 import poke, group_poke
