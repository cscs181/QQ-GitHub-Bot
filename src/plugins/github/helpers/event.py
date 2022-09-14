#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-07 11:48:48
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 06:47:22
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from src.plugins.github.libs.platform import PLATFORMS, UserInfo, GroupInfo

# handled events
QQ_USER_EVENT = (MessageEvent,)
QQ_GROUP_EVENT = (GroupMessageEvent,)
QQ_EVENT = QQ_USER_EVENT + QQ_GROUP_EVENT

USER_EVENT = QQ_USER_EVENT
GROUP_EVENT = QQ_GROUP_EVENT


def get_platform(event: Event) -> PLATFORMS | None:
    if isinstance(event, QQ_EVENT):
        return "qq"


def get_user_id(event: Event) -> int | str | None:
    if isinstance(event, QQ_USER_EVENT):
        return event.user_id


def get_user_info(event: Event) -> UserInfo | None:
    platform = get_platform(event)
    user_id = get_user_id(event)
    if platform and user_id:
        return {"type": platform, "user_id": user_id}  # type: ignore


def get_group_id(event: Event) -> int | str | None:
    if isinstance(event, QQ_GROUP_EVENT):
        return event.group_id


def get_group_info(event: Event) -> GroupInfo | None:
    platform = get_platform(event)
    group_id = get_group_id(event)
    if platform and group_id:
        return {"type": platform, "group_id": group_id}  # type: ignore
