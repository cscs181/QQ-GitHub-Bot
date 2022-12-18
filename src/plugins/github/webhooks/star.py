#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-12-18 13:44:11
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-18 14:15:47
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import asyncio
from typing import NamedTuple
from datetime import timedelta

from nonebot import on_type
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.adapters.github import StarCreated, StarDeleted

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

THROTTLE_EXPIRE = timedelta(seconds=30)

star = on_type(
    (StarCreated, StarDeleted), priority=config.github_command_priority, block=True
)


class EventInfo(NamedTuple):
    username: str
    repo_name: str
    action: str
    star_count: int


def get_event_info(event: StarCreated | StarDeleted) -> EventInfo:
    username = event.payload.sender.login
    repo_name = event.payload.repository.full_name
    action = event.payload.action
    star_count: int = event.payload.repository.stargazers_count
    return EventInfo(username, repo_name, action, star_count)


def throttle_id(event: StarCreated | StarDeleted) -> str | None:
    info = get_event_info(event)
    return f"star_event:{info.username}:{info.repo_name}:{info.action}"


@star.handle(
    parameterless=(
        Depends(Throttle((StarCreated, StarDeleted), throttle_id, THROTTLE_EXPIRE)),
    )
)
async def handle_unknown_event(event: StarCreated | StarDeleted):
    info = get_event_info(event)
    action = "starred" if info.action == "created" else "unstarred"
    message = (
        f"用户 {info.username} {action} 仓库 {info.repo_name} (共计 {info.star_count} 个 star)"
    )

    owner, repo = info.repo_name.split("/", 1)
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
