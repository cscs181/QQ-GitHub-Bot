"""
@Author         : yanyongyu
@Date           : 2022-11-07 05:14:32
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 12:28:43
@Description    : Webhook unknown event broadcast
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import asyncio
from datetime import timedelta

from nonebot.params import Depends
from nonebot import logger, on_type
from nonebot.adapters.github import Event
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github.utils import get_attr_or_item

from src.plugins.github import config
from src.plugins.github.cache.message_tag import RepoTag

from ._dependencies import (
    EVENT_INFO,
    SUBSCRIBERS,
    SEND_INTERVAL,
    Throttle,
    send_subscriber_text,
)

__plugin_meta__ = PluginMetadata(
    "GitHub 事件通知",
    "订阅 GitHub 事件来接收通知",
    "此插件为 fallback 通知\n"
    "通知示例：\n"
    "用户 yanyongyu 触发了仓库 cscs181/QQ-GitHub-Bot 的事件 star",
)

THROTTLE_EXPIRE = timedelta(seconds=60)

unknown = on_type(Event, priority=config.github_webhook_priority + 1, block=True)


@unknown.handle(parameterless=(Depends(Throttle((Event,), THROTTLE_EXPIRE)),))
async def handle_unknown_event(
    event: Event, event_info: EVENT_INFO, subscribers: SUBSCRIBERS
):
    if not subscribers:
        return

    username: str = get_attr_or_item(get_attr_or_item(event.payload, "sender"), "login")

    owner, repo, event_name, action = event_info

    message = f"用户 {username} 触发了仓库 {repo} 的事件 {event_name}" + (
        f"/{action}" if action else ""
    )

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
