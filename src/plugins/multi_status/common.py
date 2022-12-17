#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-15 08:58:50
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-17 16:40:53
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from nonebot import on_command

from src.plugins.nonebot_plugin_status import status_permission

from . import server_status

command = on_command(
    "status",
    aliases={"状态"},
    permission=status_permission,
    priority=10,
    handlers=[server_status],
)
