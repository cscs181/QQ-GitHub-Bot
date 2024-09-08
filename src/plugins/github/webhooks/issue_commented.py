"""
@Author         : yanyongyu
@Date           : 2023-04-26 18:39:12
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 12:28:07
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import asyncio
from typing import cast

from nonebot import logger, on_type
from nonebot.plugin import PluginMetadata
from playwright.async_api import Error, TimeoutError
from githubkit.versions.latest.models import SimpleInstallation
from nonebot.adapters.github import ActionTimeout, IssueCommentCreated

from src.plugins.github import config
from src.plugins.github.utils import get_github_bot
from src.plugins.github.libs.renderer import issue_commented_to_image
from src.plugins.github.cache.message_tag import IssueTag, PullRequestTag

from ._dependencies import (
    SUBSCRIBERS,
    SEND_INTERVAL,
    send_subscriber_text,
    send_subscriber_image,
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
async def handle_issue_comment_created_event(
    event: IssueCommentCreated, subscribers: SUBSCRIBERS
):
    if not subscribers:
        return

    repo_name = event.payload.repository.full_name
    owner, repo = repo_name.split("/", 1)

    if event.payload.issue.pull_request:
        tag = PullRequestTag(
            owner=owner,
            repo=repo,
            number=event.payload.issue.number,
            is_receive=False,
        )
        fallback_message = (
            f"用户 {event.payload.sender.login} 评论了 Pull Request"
            f" {repo_name}#{event.payload.issue.number}: {event.payload.issue.title}"
        )
    else:
        tag = IssueTag(
            owner=owner, repo=repo, number=event.payload.issue.number, is_receive=False
        )
        fallback_message = (
            f"用户 {event.payload.sender.login} 评论了 Issue"
            f" {repo_name}#{event.payload.issue.number}: {event.payload.issue.title}"
        )

    bot = get_github_bot()

    image = None

    try:
        installation = cast(SimpleInstallation, event.payload.installation)
        async with bot.as_installation(installation.id):
            image = await issue_commented_to_image(
                bot,
                event.payload.repository,
                event.payload.issue,
                event.payload.comment,
            )
    except (ActionTimeout, TimeoutError, Error):
        pass
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while generating issue/opened image: {e}"
        )

    for target in subscribers:
        try:
            if image is not None:
                await send_subscriber_image(target.to_subscriber_info(), image, tag)
            else:
                await send_subscriber_text(
                    target.to_subscriber_info(), fallback_message, tag
                )
        except Exception as e:
            logger.opt(exception=e).warning(
                "Send message to subscriber failed: {e}",
                target_info=target.to_subscriber_info(),
                e=e,
            )

        await asyncio.sleep(SEND_INTERVAL)
