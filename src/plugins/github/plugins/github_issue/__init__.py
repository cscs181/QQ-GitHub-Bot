#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 15:15:02
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-12 15:16:22
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import base64
from typing import Dict

from nonebot import on_regex
from httpx import HTTPStatusError
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, MessageEvent, MessageSegment

try:
    from ...libs.auth import get_user_token
except ImportError:
    get_user_token = None
from ... import github_config as config
from ...libs.issue import get_issue, issue_to_image

REPO_ISSUE_REGEX = r"^(?P<owner>[a-zA-Z0-9][a-zA-Z0-9\-]*)/(?P<repo>[a-zA-Z0-9_\-]+)#(?P<number>\d+)$"

issue = on_regex(REPO_ISSUE_REGEX, priority=config.github_command_priority)
issue.__doc__ = """
^owner/repo#number$
获取指定仓库 issue / pr
"""


@issue.handle()
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    group: Dict[str, str] = state["_matched_dict"]
    owner = group["owner"]
    repo = group["repo"]
    number = int(group["number"])
    token = None
    if get_user_token:
        token = await get_user_token(event.get_user_id())
    try:
        issue_ = await get_issue(owner, repo, number, token)
    except HTTPStatusError:
        await issue.finish(f"Issue #{number} not found for repo {owner}/{repo}")
        return
    img = await issue_to_image(issue_)
    if img:
        await issue.finish(
            MessageSegment.image(f"base64://{base64.b64encode(img).decode()}"))
