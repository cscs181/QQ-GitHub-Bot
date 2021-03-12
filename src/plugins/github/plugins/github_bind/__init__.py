#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-12 15:03:23
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-12 16:15:55
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import re

from nonebot import on_command
from httpx import HTTPStatusError
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent

from ...libs.repo import get_repo
from src.libs.utils import allow_cancel, only_group

REPO_REGEX = r"^(?P<owner>[a-zA-Z0-9][a-zA-Z0-9\-]*)/(?P<repo>[a-zA-Z0-9_\-]+)$"

bind = on_command("bind",
                  only_group,
                  permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)

bind.args_parser(allow_cancel)


@bind.handle()
async def process_arg(bot: Bot, event: GroupMessageEvent, state: T_State):
    arg = event.get_plaintext().strip()
    if arg:
        state["full_name"] = arg


@bind.got("full_name", prompt="绑定仓库的全名？(e.g. owner/repo)")
async def process_repo(bot: Bot, event: GroupMessageEvent, state: T_State):
    name = state["full_name"]
    matched = re.match(REPO_REGEX, name)
    if not matched:
        await bind.reject(f"仓库名 {name} 不合法！请重新发送或取消")
    owner = matched.group("owner")
    repo_name = matched.group("repo")
    try:
        repo = await get_repo(owner, repo_name)
    except HTTPStatusError:
        await bind.reject(f"仓库名 {owner}/{repo_name} 不存在！请重新发送或取消")
        return

    # TODO: Store
    await bind.finish(f"本群成功绑定仓库 {repo.full_name} ！")
