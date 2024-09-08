"""
@Author         : yanyongyu
@Date           : 2022-12-18 13:44:11
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 12:27:35
@Description    : Webhook star event broadcast
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import asyncio
from datetime import timedelta

from nonebot.params import Depends
from nonebot import logger, on_type
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import StarCreated, StarDeleted

from src.plugins.github import config
from src.plugins.github.cache.message_tag import RepoTag

from ._dependencies import SUBSCRIBERS, SEND_INTERVAL, Throttle, send_subscriber_text

__plugin_meta__ = PluginMetadata(
    "GitHub Star 事件通知",
    "订阅 GitHub Star 事件来接收通知",
    "通知示例：\n用户 yanyongyu starred 仓库 cscs181/QQ-GitHub-Bot (共计 6666 个 star)",
)

THROTTLE_EXPIRE = timedelta(seconds=120)

star = on_type(
    (StarCreated, StarDeleted), priority=config.github_webhook_priority, block=True
)


@star.handle(
    parameterless=(Depends(Throttle((StarCreated, StarDeleted), THROTTLE_EXPIRE)),)
)
async def handle_star_event(event: StarCreated | StarDeleted, subscribers: SUBSCRIBERS):
    if not subscribers:
        return

    username = event.payload.sender.login
    repo_name = event.payload.repository.full_name
    action = event.payload.action
    star_count: int = event.payload.repository.stargazers_count
    action_name = "starred" if action == "created" else "unstarred"
    message = (
        f"用户 {username} {action_name} 仓库 {repo_name} (共计 {star_count} 个 star)"
    )

    owner, repo = repo_name.split("/", 1)
    tag = RepoTag(owner=owner, repo=repo, is_receive=False)

    for target in subscribers:
        try:
            await send_subscriber_text(target.to_subscriber_info(), message, tag)
        except Exception as e:
            logger.opt(exception=e).warning(
                "Send message to subscriber failed: {e}",
                target_info=target.to_subscriber_info(),
                e=e,
            )

        await asyncio.sleep(SEND_INTERVAL)
