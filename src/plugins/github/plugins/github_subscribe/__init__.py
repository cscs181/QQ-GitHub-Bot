#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-15 23:14:16
@LastEditors    : yanyongyu
@LastEditTime   : 2021-05-21 15:19:19
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import re

from nonebot import on_command
from nonebot.log import logger
from httpx import HTTPStatusError
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp import GROUP_ADMIN, GROUP_OWNER, PRIVATE_FRIEND

from src.utils import allow_cancel
from ... import github_config as config
from ...libs.auth import get_user_token
from ...libs.hook import create_hook, has_hook, create_hook_url

REPO_REGEX: str = r"^(?P<owner>[a-zA-Z0-9][a-zA-Z0-9\-]*)/(?P<repo>[a-zA-Z0-9_\-\.]+)$"

subscribe = on_command("subscribe",
                       priority=config.github_command_priority,
                       permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER |
                       PRIVATE_FRIEND)
subscribe.__doc__ = """
/subscribe owner/repo
订阅仓库事件（需要权限）
"""

subscribe.args_parser(allow_cancel)


@subscribe.handle()
async def handle_arg(bot: Bot, event: MessageEvent, state: T_State):
    arg = event.get_plaintext().strip()
    if arg:
        state["full_name"] = arg


@subscribe.got("full_name", prompt="订阅仓库的全名？(e.g. owner/repo)")
async def process_repo(bot: Bot, event: MessageEvent, state: T_State):
    name = state["full_name"]
    matched = re.match(REPO_REGEX, name)
    if not matched:
        await subscribe.reject(f"仓库名 {name} 不合法！请重新发送或取消")
    owner = matched.group("owner")
    repo_name = matched.group("repo")

    token = get_user_token(event.get_user_id())
    if not token:
        await subscribe.finish(f"请先使用 /auth 命令授权你的 GitHub 账号")
        return

    try:
        if not await has_hook(f"{owner}/{repo_name}", token):
            url = create_hook_url(f"{owner}/{repo_name}")
            await create_hook(
                f"{owner}/{repo_name}", {
                    "url": url,
                    "content_type": "json",
                    "insecure_ssl": not config.github_self_ssl
                }, token, ["issues", "issue_comment", "pull_request"])
    except HTTPStatusError as e:
        if e.response.status_code == 403:
            await subscribe.finish(f"你无权操作仓库 {owner}/{repo_name}！")
            return
        elif e.response.status_code == 404:
            await subscribe.reject(f"仓库名 {owner}/{repo_name} 不存在！请重新发送或取消")
            return
        logger.opt(colors=True,
                   exception=e).error(f"github_subscribe: create_hook")
        await subscribe.finish("订阅仓库时发生错误，请联系开发者或重试")
        return

    # TODO: subscribe repo with (repo, user, bot) info
    await subscribe.finish(f"成功订阅仓库 {owner}/{repo_name}！")
