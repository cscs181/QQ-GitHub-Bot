#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 07:29:52
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-07 07:37:24
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Bot

from src.plugins.github.utils import get_qq_bot, get_qqguild_bot
from src.plugins.github.models import User, Group, UserSubscription, GroupSubscription

USER_BOT_MAPPINGS = {
    "qq_id": get_qq_bot,
    "qqguild_id": get_qqguild_bot,
}

GROUP_BOT_MAPPINGS = {
    "group_id": get_qq_bot,
    "qqguild_channel": get_qqguild_bot,
}


def get_user_bot(user: User | UserSubscription) -> Bot:
    for key, value in USER_BOT_MAPPINGS.items():
        if getattr(user, key):
            return value()
    raise ValueError("Invalid user")


def get_group_bot(group: Group | GroupSubscription) -> Bot:
    for key, value in GROUP_BOT_MAPPINGS.items():
        if getattr(group, key):
            return value()
    raise ValueError("Invalid group")
