#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-12 15:03:23
@LastEditors    : yanyongyu
@LastEditTime   : 2022-01-26 18:11:58
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import re

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from httpx import HTTPStatusError, TimeoutException
from nonebot.adapters.onebot.v11 import (
    GROUP_ADMIN,
    GROUP_OWNER,
    Bot,
    GroupMessageEvent,
)

from src.utils import only_group, allow_cancel

from ...libs.repo import get_repo
from ... import github_config as config
from ...libs.redis import (
    get_group_bind_repo,
    set_group_bind_repo,
    delete_group_bind_repo,
    exists_group_bind_repo,
)

# allow using api without token
try:
    from ...libs.auth import get_user_token
except ImportError:
    get_user_token = None

REPO_REGEX: str = (
    r"^(?P<owner>[a-zA-Z0-9][a-zA-Z0-9\-]*)/(?P<repo>[a-zA-Z0-9_\-\.]+)$"
)

bind = on_command(
    "bind",
    only_group,
    priority=config.github_command_priority,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
)
bind.__doc__ = """
/bind owner/repo
绑定当前群与指定仓库
/bind
查询当前绑定的仓库
"""

bind.args_parser(allow_cancel)


@bind.handle()
async def process_arg(bot: Bot, event: GroupMessageEvent, state: T_State):
    arg = event.get_plaintext().strip()
    if arg:
        state["full_name"] = arg


@bind.handle()
async def check_exists(bot: Bot, event: GroupMessageEvent, state: T_State):
    if "full_name" in state:
        return

    exist_repo = get_group_bind_repo(str(event.group_id))
    if exist_repo:
        await bind.finish(f"当前已绑定仓库：{exist_repo}")


@bind.got("full_name", prompt="绑定仓库的全名？(e.g. owner/repo)")
async def process_repo(bot: Bot, event: GroupMessageEvent, state: T_State):
    name = state["full_name"]
    matched = re.match(REPO_REGEX, name)
    if not matched:
        await bind.reject(f"仓库名 {name} 不合法！请重新发送或取消")
    owner = matched.group("owner")
    repo_name = matched.group("repo")
    token = None
    if get_user_token:
        token = get_user_token(event.get_user_id())
    try:
        repo = await get_repo(owner, repo_name, token)
    except TimeoutException:
        await bind.finish(f"获取仓库数据超时！请尝试重试")
    except HTTPStatusError:
        await bind.reject(f"仓库名 {owner}/{repo_name} 不存在！请重新发送或取消")

    set_group_bind_repo(str(event.group_id), repo.full_name)
    await bind.finish(f"本群成功绑定仓库 {repo.full_name} ！")


unbind = on_command(
    "unbind",
    only_group,
    priority=config.github_command_priority,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
)
unbind.__doc__ = """
/unbind
解绑当前群和指定仓库
"""


@unbind.handle()
async def process_unbind(bot: Bot, event: GroupMessageEvent):
    if exists_group_bind_repo(str(event.group_id)):
        delete_group_bind_repo(str(event.group_id))
        await unbind.finish("成功解绑仓库！")
    else:
        await unbind.finish("尚未绑定仓库！")
