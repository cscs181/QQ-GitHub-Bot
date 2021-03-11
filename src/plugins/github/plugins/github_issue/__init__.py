#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 15:15:02
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-12 01:02:56
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import base64
from pathlib import Path
from typing import Dict, List

import markdown
from nonebot import on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, MessageEvent, MessageSegment

from src.libs import html2img
from src.libs.github import Github
from ... import github_config as config

HEADER = """
# {title} <font color=#8b949e>#{number}</font>

<span class="State State--{status}">{status}</span> <small><font color=#8b949e>{comments} comments</font></small>

### **{login}** <small><font color=#8b949e>{updated_at}</font></small>
"""
OPTIONS: dict = {"encoding": "utf-8"}
CSS_FILES: List[str] = [
    str(Path(__file__).parent / "github.css"),
    str(Path(__file__).parent / "status.css")
]

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
    await g.close()
    if issue_.body_html:
        html = '<article class="markdown-body">' + markdown.markdown(
            HEADER.format(
                title=issue_.title,
                number=issue_.number,
                status=issue_.state,
                comments=issue_.comments,
                login=issue_.user.login,
                updated_at=issue_.updated_at.strftime(
                    "%Y-%m-%d %H:%M:%S"))) + issue_.body_html + "</article>"
        img = await html2img.from_string(html, options=OPTIONS, css=CSS_FILES)
    elif issue_.body:
        html = '<article class="markdown-body">' + markdown.markdown(
            HEADER.format(title=issue_.title,
                          number=issue_.number,
                          status=issue_.state,
                          comments=issue_.comments,
                          login=issue_.user.login,
                          updated_at=issue_.updated_at.strftime(
                              "%Y-%m-%d %H:%M:%S")) +
            issue_.body) + "</article>"
        img = await html2img.from_string(html, options=OPTIONS, css=CSS_FILES)
    else:
        return
    await issue.finish(
        MessageSegment.image(f"base64://{base64.b64encode(img).decode()}"))
