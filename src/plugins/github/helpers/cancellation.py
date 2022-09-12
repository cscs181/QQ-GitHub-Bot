#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-07 12:14:01
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-07 12:15:50
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import re

from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import Depends, EventMessage

CHINESE_CANCELLATION_WORDS = {"算", "别", "不", "停", "取消"}
CHINESE_CANCELLATION_REGEX_1 = re.compile(r"^那?[算别不停]\w{0,3}了?吧?$")
CHINESE_CANCELLATION_REGEX_2 = re.compile(r"^那?(?:[给帮]我)?取消了?吧?$")


def is_cancellation(message: Message | str) -> bool:
    text = message.extract_plain_text() if isinstance(message, Message) else message
    return any(kw in text for kw in CHINESE_CANCELLATION_WORDS) and bool(
        CHINESE_CANCELLATION_REGEX_1.match(text)
        or CHINESE_CANCELLATION_REGEX_2.match(text)
    )


def allow_cancellation(cancel_prompt: str | None = None) -> bool:
    async def dependency(matcher: Matcher, message: Message = EventMessage()) -> bool:
        cancelled = is_cancellation(message)
        if cancelled and cancel_prompt:
            await matcher.finish(cancel_prompt)
        return not cancelled

    return Depends(dependency)
