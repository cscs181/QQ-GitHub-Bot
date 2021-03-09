#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 15:15:02
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-09 16:37:02
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import base64
from typing import Dict

from nonebot import on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, MessageEvent, MessageSegment

from src.libs import md2img
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
    number = group["number"]
    # TODO: Get user token (optional)
    token = None
    # TODO: Get issue content
    issue_content = ""
    img = await md2img.from_string(issue_content)
    await issue.finish(MessageSegment.image(f"base64://{base64.b64encode(img)}")
                      )
