#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-26 15:35:46
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-26 15:39:49
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.matcher import Matcher

from src.plugins.github.models import GroupSubscription


async def bypass_create(matcher: Matcher) -> None:
    if matcher.get_arg("events") is not None:
        matcher.skip()


async def list_current_subscriptions() -> list[GroupSubscription]:
    return []
