import asyncio
from typing import cast

from nonebot import logger, on_type
from nonebot.plugin import PluginMetadata
from githubkit.webhooks import InstallationLite
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.github import IssuesClosed, ActionTimeout, PullRequestClosed

from src.plugins.github import config
from src.plugins.github.libs.renderer import issue_closed_to_image
from src.plugins.github.utils import get_github_bot, set_context_bot
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
    "GitHub Issue/PullRequest 关闭事件通知",
    "订阅 GitHub issue/closed pull_request/closed 事件来接收通知",
    "通知以图片形式发送",
)

issue_closed = on_type(
    (IssuesClosed, PullRequestClosed),
    priority=config.github_webhook_priority,
    block=True,
)


@issue_closed.handle()
async def handle_issue_closed_event(event: IssuesClosed | PullRequestClosed):
    repo_name = event.payload.repository.full_name
    owner, repo = repo_name.split("/", 1)

    if isinstance(event, IssuesClosed):
        tag = IssueTag(
            owner=owner, repo=repo, number=event.payload.issue.number, is_receive=False
        )
        fallback_message = (
            f"用户 {event.payload.sender.login} 关闭了 Issue"
            f" {repo_name}#{event.payload.issue.number}: {event.payload.issue.title}"
        )
        issue = event.payload.issue
    else:
        tag = PullRequestTag(
            owner=owner,
            repo=repo,
            number=event.payload.pull_request.number,
            is_receive=False,
        )
        fallback_message = (
            f"用户 {event.payload.sender.login} 关闭了 Pull Request"
            f" {repo_name}#{event.payload.pull_request.number}:"
            f" {event.payload.pull_request.title}"
        )
        issue = event.payload.pull_request

    bot = get_github_bot()

    image = None

    try:
        installation = cast(InstallationLite, event.payload.installation)
        async with bot.as_installation(installation.id):
            with set_context_bot(bot):
                image = await issue_closed_to_image(event.payload.repository, issue)
    except (ActionTimeout, TimeoutError, Error):
        pass
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while generating issue/closed image: {e}"
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
