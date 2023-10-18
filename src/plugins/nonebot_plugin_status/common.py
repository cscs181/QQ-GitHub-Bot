"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:00:13
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 18:26:14
@Description    : Common text matcher for status plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot import on_command

from . import server_status, status_config, status_permission

if status_config.server_status_enabled:
    command = on_command(
        "status",
        aliases={"状态"},
        permission=status_permission,
        priority=10,
        handlers=[server_status],
    )
    """`status`/`状态` command matcher"""
