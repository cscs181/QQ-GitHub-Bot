#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2023-04-26 18:39:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-04-26 18:45:25
@Description    : None
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
from nonebot.adapters.github import ActionTimeout, IssueCommentCreated

from src.plugins.github import config
from src.plugins.github.utils import get_github_bot, set_context_bot
from src.plugins.github.libs.renderer import issue_commented_to_image
from src.plugins.github.libs.message_tag import IssueTag, PullRequestTag
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
    "GitHub Issue/PullRequest 评论事件通知",
    "订阅 GitHub issue_comment/created 事件来接收通知",
    "通知以图片形式发送",
)

issue_commented = on_type(
    (IssueCommentCreated,),
    priority=config.github_webhook_priority,
    block=True,
)


@issue_commented.handle()
async def handle_issue_opened_event(event: IssueCommentCreated):
    repo_name = event.payload.repository.full_name
    owner, repo = repo_name.split("/", 1)

    if event.payload.issue.pull_request:
        tag = PullRequestTag(
            owner=owner,
            repo=repo,
            number=event.payload.issue.number,
            is_receive=False,
        )
        fallback_message = f"用户 {event.payload.sender.login} 评论了 Pull Request {repo_name}#{event.payload.issue.number}: {event.payload.issue.title}"
    else:
        tag = IssueTag(
            owner=owner, repo=repo, number=event.payload.issue.number, is_receive=False
        )
        fallback_message = f"用户 {event.payload.sender.login} 评论了 Issue {repo_name}#{event.payload.issue.number}: {event.payload.issue.title}"

    bot = get_github_bot()

    image = None

    try:
        installation = cast(InstallationLite, event.payload.installation)
        async with bot.as_installation(installation.id):
            with set_context_bot(bot):
                image = await issue_commented_to_image(
                    event.payload.repository, event.payload.issue, event.payload.comment
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
            logger.opt(exception=e).warning(f"Send message to user {user} failed: {e}")
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
            logger.opt(exception=e).warning(
                f"Send message to group {group} failed: {e}"
            )
        await asyncio.sleep(SEND_INTERVAL)
