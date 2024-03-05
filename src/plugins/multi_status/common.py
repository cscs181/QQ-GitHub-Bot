"""
@Author         : yanyongyu
@Date           : 2022-10-15 08:58:50
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:24:33
@Description    : Common text matcher for multi pod status plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"


from nonebot import on_command
from nonebot_plugin_status import status_permission

from . import server_status

command = on_command(
    "status",
    aliases={"状态"},
    permission=status_permission,
    priority=10,
    handlers=[server_status],
)
