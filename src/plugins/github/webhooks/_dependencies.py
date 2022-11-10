#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 08:35:10
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-10 12:16:38
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.log import logger
from nonebot.adapters import Bot
from nonebot.adapters.github import Event
from nonebot.adapters.onebot.v11 import Bot as QQBot
from nonebot.adapters.github.utils import get_attr_or_item
from nonebot.adapters.onebot.v11 import Message as QQMessage
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.github.models import UserSubscription, GroupSubscription
from src.plugins.github.libs.message_tag import Tag, MessageInfo, create_message_tag
from src.plugins.github.libs.platform import (
    list_subscribed_users,
    list_subscribed_groups,
)

SEND_INTERVAL = 0.5


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
