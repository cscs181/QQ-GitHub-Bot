#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:31:37
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-06 03:43:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.typing import T_State

from src.plugins.github import config
from src.plugins.github.helpers import get_platform
from src.plugins.github.libs.message_tag import (
    Tag,
    IssueTag,
    CommitTag,
    PullRequestTag,
    create_message_tag,
)

from . import KEY_GITHUB_REPLY, is_github_reply

link = on_command(
    "link", is_github_reply, priority=config.github_command_priority, block=True
)


@link.handle()
async def handle_link(event: Event, state: T_State):
    tag: Tag = state[KEY_GITHUB_REPLY]
    url = f"https://github.com/{tag.owner}/{tag.repo}"
    match tag:
        case IssueTag():
            url += f"/issues/{tag.number}"
        case PullRequestTag():
            url += f"/pull/{tag.number}"
        case CommitTag():
            url += f"/commit/{tag.commit}"

    result = await link.send(url)

    match get_platform(event):
        case "qq":
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
