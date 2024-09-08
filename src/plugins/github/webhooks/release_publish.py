"""
@Author         : yanyongyu
@Date           : 2023-04-04 20:02:19
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 12:28:26
@Description    : Webhook release publish broadcast
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import asyncio

from nonebot import logger, on_type
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ReleasePublished

from src.plugins.github import config
from src.plugins.github.cache.message_tag import ReleaseTag
from src.plugins.github.libs.opengraph import get_opengraph_image

from ._dependencies import (
    SUBSCRIBERS,
    SEND_INTERVAL,
    send_subscriber_text,
    send_subscriber_image,
)

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
    if not subscribers:
        return

    owner = event.payload.repository.owner.login
    repo = event.payload.repository.name

    tag = ReleaseTag(
        owner=owner, repo=repo, tag=event.payload.release.tag_name, is_receive=False
    )

    image = await get_opengraph_image(tag)

    fallback_msg = f"Release [{tag.tag}] published in {owner}/{repo}"

    for target in subscribers:
        try:
            if image:
                await send_subscriber_image(target.to_subscriber_info(), image, tag)
            else:
                await send_subscriber_text(
                    target.to_subscriber_info(), fallback_msg, tag
                )
        except Exception as e:
            logger.opt(exception=e).warning(
                "Send message to subscriber failed: {e}",
                target_info=target.to_subscriber_info(),
                e=e,
            )

        await asyncio.sleep(SEND_INTERVAL)
