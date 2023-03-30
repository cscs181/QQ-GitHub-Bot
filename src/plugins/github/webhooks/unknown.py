#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 05:14:32
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-31 00:13:09
@Description    : Webhook unknown event broadcast
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import asyncio
from typing import NamedTuple
from datetime import timedelta

from nonebot import on_type
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.adapters.github import Event
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github.utils import get_attr_or_item

from src.plugins.github import config
from src.plugins.github.libs.message_tag import RepoTag
from src.plugins.github.libs.platform import get_user_bot, get_group_bot

from ._dependencies import (
    SEND_INTERVAL,
    Throttle,
    send_user_text,
    send_group_text,
    get_subscribed_users,
    get_subscribed_groups,
)

__plugin_meta__ = PluginMetadata(
    "GitHub 事件通知",
    "订阅 GitHub 事件来接收通知",
    (
        "此插件为 fallback 通知\n"
        "通知示例：\n"
        "用户 yanyongyu 触发了仓库 cscs181/QQ-GitHub-Bot 的事件 star"
    ),
)

THROTTLE_EXPIRE = timedelta(seconds=60)

unknown = on_type(Event, priority=config.github_webhook_priority + 1, block=True)


class EventInfo(NamedTuple):
    username: str
    repo_name: str | None
    event_name: str
    action: str | None


def get_event_info(event: Event) -> EventInfo:
    username: str = get_attr_or_item(get_attr_or_item(event.payload, "sender"), "login")
    action: str | None = get_attr_or_item(event.payload, "action")
    repository = get_attr_or_item(event.payload, "repository")
    repo_name = None
    if repository is not None:
        repo_name = get_attr_or_item(repository, "full_name")
    return EventInfo(username, repo_name, event.name, action)


@unknown.handle(parameterless=(Depends(Throttle((Event,), THROTTLE_EXPIRE)),))
async def handle_unknown_event(event: Event):
    repository = get_attr_or_item(event.payload, "repository")
    if repository is None:
        return

    username: str = get_attr_or_item(get_attr_or_item(event.payload, "sender"), "login")
    repo_name: str = get_attr_or_item(repository, "full_name")
    action: str | None = get_attr_or_item(event.payload, "action")
    message = f"用户 {username} 触发了仓库 {repo_name} 的事件 {event.name}" + (
        f"/{action}" if action else ""
    )

    owner, repo = repo_name.split("/", 1)
    tag = RepoTag(owner=owner, repo=repo, is_receive=False)

    for user in await get_subscribed_users(event):
        try:
            await send_user_text(user, get_user_bot(user), message, tag)
        except Exception as e:
            logger.warning(f"Send message to user {user} failed: {e}")
        await asyncio.sleep(SEND_INTERVAL)

    for group in await get_subscribed_groups(event):
        try:
            await send_group_text(group, get_group_bot(group), message, tag)
        except Exception as e:
            logger.warning(f"Send message to group {group} failed: {e}")
        await asyncio.sleep(SEND_INTERVAL)
