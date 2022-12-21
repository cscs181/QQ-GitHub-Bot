#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-27 04:24:58
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:46:17
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.rule import Rule
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.adapters.github import Event as GitHubEvent

from .event import GROUP_EVENT, PRIVATE_EVENT


def is_private_event(event: Event) -> bool:
    return isinstance(event, PRIVATE_EVENT)


def is_group_event(event: Event) -> bool:
    return isinstance(event, GROUP_EVENT)


# no github rule
async def no_github_event(event: Event):
    return not isinstance(event, GitHubEvent)


NO_GITHUB_EVENT = Rule(no_github_event)


async def run_when_private(event: Event, matcher: Matcher) -> None:
    if not is_private_event(event):
        matcher.skip()


async def run_when_group(event: Event, matcher: Matcher) -> None:
    if not is_group_event(event):
        matcher.skip()
