#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 05:14:32
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-05 13:02:08
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import asyncio

from nonebot import on_type
from nonebot.adapters.github import Event
from nonebot.adapters.github.utils import get_attr_or_item

from src.plugins.github import config
from src.plugins.github.libs.message_tag import RepoTag
from src.plugins.github.libs.platform import get_user_bot, get_group_bot

from ._dependencies import (
    SEND_INTERVAL,
    send_user_text,
    send_group_text,
    get_subscribed_users,
    get_subscribed_groups,
)

unknown = on_type(Event, priority=config.github_command_priority + 10)


@unknown.handle()
async def handle_unknown_event(event: Event):
    username: str = get_attr_or_item(get_attr_or_item(event, "sender"), "login")
    action: str | None = get_attr_or_item(event.payload, "action")
    repository = get_attr_or_item(event.payload, "repository")
    if repository is None:
        return
    repo_name: str = get_attr_or_item(repository, "full_name")
    message = f"用户 {username} 触发了仓库 {repo_name} 的事件 {event.name}" + (
        f"/{action}" if action else ""
    )

    owner, repo = repo_name.split("/", 1)
    tag = RepoTag(owner=owner, repo=repo, is_receive=False)

    for user in await get_subscribed_users(event):
        await send_user_text(user, get_user_bot(user), message, tag)
        await asyncio.sleep(SEND_INTERVAL)

    for group in await get_subscribed_groups(event):
        await send_group_text(group, get_group_bot(group), message, tag)
        await asyncio.sleep(SEND_INTERVAL)
