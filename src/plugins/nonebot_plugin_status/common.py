#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-15 09:39:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command

from . import server_status, status_config, status_permission

if status_config.server_status_enabled:
    command = on_command(
        "状态", permission=status_permission, priority=10, handlers=[server_status]
    )
