#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2023-04-04 20:02:19
@LastEditors    : yanyongyu
@LastEditTime   : 2023-04-05 01:05:17
@Description    : Webhook issue create broadcast
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import asyncio
from typing import cast

from nonebot import on_type
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from githubkit.webhooks import InstallationLite
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.github import IssuesOpened, ActionTimeout

from src.plugins.github import config
from src.plugins.github.libs.message_tag import IssueTag
from src.plugins.github.libs.renderer import issue_opened_to_image
from src.plugins.github.utils import get_github_bot, set_context_bot
from src.plugins.github.libs.platform import get_user_bot, get_group_bot

from ._dependencies import (
    SEND_INTERVAL,
    send_user_text,
    send_group_text,
    send_user_image,
    send_group_image,
    get_subscribed_users,
    get_subscribed_groups,
)

__plugin_meta__ = PluginMetadata(
    "GitHub Issue 创建事件通知",
    "订阅 GitHub issue/opened 事件来接收通知",
    "通知以图片形式发送",
)

issues = on_type(IssuesOpened, priority=config.github_webhook_priority, block=True)


@issues.handle()
async def handle_issues_opened_event(event: IssuesOpened):
    repo_name = event.payload.repository.full_name
    owner, repo = repo_name.split("/", 1)
    tag = IssueTag(
        owner=owner, repo=repo, number=event.payload.issue.number, is_receive=False
    )

    bot = get_github_bot()

    image = None
    fallback_message = f"用户 {event.payload.sender.login} 创建了 Issue {repo_name}#{event.payload.issue.number}: {event.payload.issue.title}"

    try:
        installation = cast(InstallationLite, event.payload.installation)
        async with bot.as_installation(installation.id):
            with set_context_bot(bot):
                image = await issue_opened_to_image(
                    event.payload.repository, event.payload.issue
                )
    except (ActionTimeout, TimeoutError, Error):
        pass
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while generating issue/opened image: {e}"
        )

    for user in await get_subscribed_users(event):
        try:
            if image is not None:
                await send_user_image(user, get_user_bot(user), image, tag)
            else:
                await send_user_text(user, get_user_bot(user), fallback_message, tag)
        except Exception as e:
            logger.warning(f"Send message to user {user} failed: {e}")
        await asyncio.sleep(SEND_INTERVAL)

    for group in await get_subscribed_groups(event):
        try:
            if image is not None:
                await send_group_image(group, get_group_bot(group), image, tag)
            else:
                await send_group_text(
                    group, get_group_bot(group), fallback_message, tag
                )
        except Exception as e:
            logger.warning(f"Send message to group {group} failed: {e}")
        await asyncio.sleep(SEND_INTERVAL)
