#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import secrets

from nonebot import on_type
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ReleasePublished

from src.plugins.github import config
from src.plugins.github.libs.message_tag import RepoTag
from src.plugins.github.libs.platform import get_user_bot, get_group_bot

from ._dependencies import (
    SEND_INTERVAL,
    send_user_image_url,
    get_subscribed_users,
    send_group_image_url,
    get_subscribed_groups,
)

__plugin_meta__ = PluginMetadata(
    "GitHub Release 发布事件通知",
    "订阅 GitHub release/published 事件来接收通知",
    "通知以图片形式发送",
)

release = on_type(ReleasePublished, priority=config.github_webhook_priority, block=True)


@release.handle()
async def handle_release_published_event(event: ReleasePublished):
    repo_name = event.payload.repository.full_name
    owner, repo = repo_name.split("/", 1)
    tag = RepoTag(owner=owner, repo=repo, is_receive=False)

    image_url = (
        f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
        f"{owner}/{repo}/releases/tag/{event.payload.release.tag_name}"
    )

    for user in await get_subscribed_users(event):
        try:
            await send_user_image_url(user, get_user_bot(user), image_url, tag)
        except Exception as e:
            logger.warning(f"Send message to user {user} failed: {e}")
        await asyncio.sleep(SEND_INTERVAL)

    for group in await get_subscribed_groups(event):
        try:
            await send_group_image_url(group, get_group_bot(group), image_url, tag)
        except Exception as e:
            logger.warning(f"Send message to group {group} failed: {e}")
        await asyncio.sleep(SEND_INTERVAL)
