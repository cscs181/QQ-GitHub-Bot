#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 08:35:10
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-18 14:14:47
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import timedelta
from typing import Generic, TypeVar, Callable, Awaitable

from nonebot.log import logger
from nonebot.adapters import Bot
from nonebot.matcher import Matcher
from nonebot.adapters.github import Event
from nonebot.adapters.onebot.v11 import Bot as QQBot
from nonebot.adapters.github.utils import get_attr_or_item
from nonebot.adapters.onebot.v11 import Message as QQMessage
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.redis import redis_client
from src.plugins.github.models import UserSubscription, GroupSubscription
from src.plugins.github.libs.message_tag import Tag, MessageInfo, create_message_tag
from src.plugins.github.libs.platform import (
    list_subscribed_users,
    list_subscribed_groups,
)

T = TypeVar("T", bound=Event)

SEND_INTERVAL = 0.5
THROTTLE_KEY = "cache:github:webhooks:throttle:{identity}"


async def get_subscribed_users(event: Event) -> list[UserSubscription]:
    repository = get_attr_or_item(event.payload, "repository")
    owner, repo = get_attr_or_item(repository, "full_name").split("/", 1)
    action = get_attr_or_item(event.payload, "action")
    return (
        await list_subscribed_users(owner, repo, event.name, action)
        if all((owner, repo, event.name))
        else []
    )


async def get_subscribed_groups(event: Event) -> list[GroupSubscription]:
    repository = get_attr_or_item(event.payload, "repository")
    owner, repo = get_attr_or_item(repository, "full_name").split("/", 1)
    action = get_attr_or_item(event.payload, "action")
    return (
        await list_subscribed_groups(owner, repo, event.name, action)
        if all((owner, repo, event.name))
        else []
    )


async def send_user_text(user: UserSubscription, bot: Bot, text: str, tag: Tag):
    if isinstance(bot, QQBot):
        result = await bot.send_private_msg(user_id=user.qq_id, message=text)
        if isinstance(result, dict) and "message_id" in result:
            await create_message_tag(
                MessageInfo(type="qq", message_id=result["message_id"]), tag
            )
    else:
        logger.error(f"Unprocessed bot type: {type(bot)}")


async def send_user_image(user: UserSubscription, bot: Bot, image: bytes, tag: Tag):
    if isinstance(bot, QQBot):
        result = await bot.send_private_msg(
            user_id=user.qq_id, message=QQMessage(QQMS.image(image))
        )
        if isinstance(result, dict) and "message_id" in result:
            await create_message_tag(
                MessageInfo(type="qq", message_id=result["message_id"]), tag
            )
    else:
        logger.error(f"Unprocessed bot type: {type(bot)}")


async def send_group_text(group: GroupSubscription, bot: Bot, text: str, tag: Tag):
    if isinstance(bot, QQBot):
        result = await bot.send_group_msg(group_id=group.qq_group, message=text)
        if isinstance(result, dict) and "message_id" in result:
            await create_message_tag(
                MessageInfo(type="qq", message_id=result["message_id"]), tag
            )
    else:
        logger.error(f"Unprocessed bot type: {type(bot)}")


async def send_group_image(group: GroupSubscription, bot: Bot, image: bytes, tag: Tag):
    if isinstance(bot, QQBot):
        result = await bot.send_group_msg(
            group_id=group.qq_group, message=QQMessage(QQMS.image(image))
        )
        if isinstance(result, dict) and "message_id" in result:
            await create_message_tag(
                MessageInfo(type="qq", message_id=result["message_id"]), tag
            )
    else:
        logger.error(f"Unprocessed bot type: {type(bot)}")


class Throttle(Generic[T]):
    def __init__(
        self,
        event_type: tuple[type[T], ...],
        identity_func: Callable[[T], str | None],
        expire: timedelta,
    ):
        self.event_type = event_type
        self.identity_func = identity_func
        self.expire = expire

    async def __call__(self, event: Event, matcher: Matcher):
        # do nothing to other event
        if not isinstance(event, self.event_type):
            return

        # get event identity
        try:
            identity = self.identity_func(event)
        except Exception as e:
            logger.warning(f"Error when getting identity: {e}")
            return

        # do nothing to event without identity
        if identity is None:
            return

        # check exists identity
        exists = await redis_client.get(THROTTLE_KEY.format(identity=identity))
        if exists is not None:
            matcher.skip()
        else:
            await redis_client.set(
                THROTTLE_KEY.format(identity=identity), 1, ex=self.expire
            )
