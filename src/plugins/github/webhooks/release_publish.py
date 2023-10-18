"""
@Author         : yanyongyu
@Date           : 2023-04-04 20:02:19
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 18:00:51
@Description    : Webhook release publish broadcast
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import asyncio
import secrets

from nonebot import logger, on_type
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ReleasePublished

from src.plugins.github import config
from src.plugins.github.cache.message_tag import RepoTag

from ._dependencies import SUBSCRIBERS, SEND_INTERVAL, send_subscriber_image_url

__plugin_meta__ = PluginMetadata(
    "GitHub Release 发布事件通知",
    "订阅 GitHub release/published 事件来接收通知",
    "通知以图片形式发送",
)

release = on_type(ReleasePublished, priority=config.github_webhook_priority, block=True)


@release.handle()
async def handle_release_published_event(
    event: ReleasePublished, subscribers: SUBSCRIBERS
):
    owner = event.payload.repository.owner.login
    repo = event.payload.repository.name
    tag = RepoTag(owner=owner, repo=repo, is_receive=False)

    image_url = (
        f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
        f"{owner}/{repo}/releases/tag/{event.payload.release.tag_name}"
    )

    for target in subscribers:
        try:
            await send_subscriber_image_url(target.to_subscriber_info(), image_url, tag)
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Send message to subscriber failed: {e}",
                target_info=target.to_subscriber_info(),
            )

        await asyncio.sleep(SEND_INTERVAL)
