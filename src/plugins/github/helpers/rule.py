#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-27 04:24:58
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-27 04:57:30
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Event
from nonebot.matcher import Matcher

from .event import GROUP_EVENT, PRIVATE_EVENT


def is_private_event(event: Event) -> bool:
    return isinstance(event, PRIVATE_EVENT)


def is_group_event(event: Event) -> bool:
    return isinstance(event, GROUP_EVENT)


async def run_when_private(event: Event, matcher: Matcher) -> None:
    if not is_private_event(event):
        matcher.skip()


async def run_when_group(event: Event, matcher: Matcher) -> None:
    if not is_group_event(event):
        matcher.skip()
