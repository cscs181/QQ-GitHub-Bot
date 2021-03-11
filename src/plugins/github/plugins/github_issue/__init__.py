#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 15:15:02
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-11 19:17:05
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import base64
from typing import Dict

from nonebot import on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, MessageEvent, MessageSegment

from src.libs.github import Github
from src.libs import html2img, md2img
from ... import github_config as config

issue = on_regex(
    r"^(?P<owner>[a-zA-Z0-9][a-zA-Z0-9\-]*)/(?P<repo>[a-zA-Z0-9_\-]+)#(?P<number>\d+)$",
    priority=config.github_command_priority)
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
    # TODO: Get user token (optional)
    token = None
    if not token:
        g = Github(config.github_client_id, config.github_client_secret)
    else:
        g = Github(token)
    repo = await g.get_repo(f"{owner}/{repo}", True)
    issue_ = await repo.get_issue(number)
    if issue_.body_html:
        img = await html2img.from_string(issue_.body_html)
    elif issue_.body:
        img = await md2img.from_string(issue_.body)
    else:
        return
    await issue.finish(MessageSegment.image(f"base64://{base64.b64encode(img)}")
                      )
