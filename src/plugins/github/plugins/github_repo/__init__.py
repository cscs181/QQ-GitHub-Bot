#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-04-26 18:19:15
@LastEditors    : yanyongyu
@LastEditTime   : 2021-08-19 23:28:16
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import secrets
from typing import Dict

from nonebot import on_regex
from nonebot.typing import T_State
from httpx import HTTPStatusError, TimeoutException
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent,
)

from ... import config as config
from ...libs.repo import get_repo
from ...utils import send_github_message

# allow using api without token
try:
    from ...libs.auth import get_user_token
except ImportError:
    get_user_token = None

ISSUE_REGEX = r"^#(?P<number>\d+)$"
REPO_REGEX: str = (
    r"^(?P<owner>[a-zA-Z0-9][a-zA-Z0-9\-]*)/" r"(?P<repo>[a-zA-Z0-9_\-\.]+)$"
)
GITHUB_LINK_REGEX = (
    r"github\.com/"
    r"(?P<owner>[a-zA-Z0-9][a-zA-Z0-9\-]*)/"
    r"(?P<repo>[a-zA-Z0-9_\-\.]+)"
)

issue = on_regex(REPO_REGEX, priority=config.github_command_priority)
issue.__doc__ = """
^owner/repo$
获取指定仓库封面
"""
# lower priority than issue link
link = on_regex(GITHUB_LINK_REGEX, priority=config.github_command_priority + 1)
link.__doc__ = """
github.com/owner/repo
识别链接获取仓库封面
"""


@issue.handle()
@link.handle()
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    group: Dict[str, str] = state["_matched_dict"]
    owner = group["owner"]
    repo = group["repo"]
    token = None
    if get_user_token:
        token = get_user_token(event.get_user_id())
    try:
        repo_ = await get_repo(owner, repo, token)
    except (HTTPStatusError, TimeoutException):
        return

    if not repo_.private:
        await issue.finish(
            MessageSegment.image(
                "https://opengraph.githubassets.com/"
                f"{secrets.token_urlsafe(16)}/{repo_.full_name}"
            )
        )
