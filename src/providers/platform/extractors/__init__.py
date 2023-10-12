"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:19:50
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 14:01:43
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any, cast

from nonebot.adapters import Bot, Event

from src.providers.platform.messages import MessageInfo
from src.providers.platform.targets import UserInfo, GroupInfo, TargetInfo

from ._base import Extractor as Extractor
from .onebot import OneBotExtractor as OneBotExtractor

EXTRACTORS = cast(tuple[type[Extractor], ...], (OneBotExtractor,))

USER_EVENTS = cast(tuple[type[Event], ...], tuple(e.USER_EVENTS for e in EXTRACTORS))
GROUP_EVENTS = cast(tuple[type[Event], ...], tuple(e.GROUP_EVENTS for e in EXTRACTORS))
MESSAGE_EVENTS = cast(
    tuple[type[Event], ...], tuple(e.MESSAGE_EVENTS for e in EXTRACTORS)
)
REPLY_EVENTS = cast(tuple[type[Event], ...], tuple(e.REPLY_EVENTS for e in EXTRACTORS))


def extract_user(event: Event) -> UserInfo | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.USER_EVENTS):
            return extractor.extract_user(event)


def extract_group(event: Event) -> GroupInfo | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.GROUP_EVENTS):
            return extractor.extract_group(event)


def extract_target(event: Event) -> TargetInfo | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.USER_EVENTS):
            return extractor.extract_target(event)


def extract_is_private(event: Event) -> bool | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.USER_EVENTS):
            return extractor.extract_is_private(event)


def extract_message(event: Event) -> MessageInfo | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.MESSAGE_EVENTS):
            return extractor.extract_message(event)


def extract_reply_message(event: Event) -> MessageInfo | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.REPLY_EVENTS):
            return extractor.extract_reply_message(event)


def get_target_bot(target: TargetInfo) -> Bot | None:
    for extractor in EXTRACTORS:
        if target.type in extractor.TARGETS:
            return extractor.get_target_bot(target)


def extract_sent_message(target: TargetInfo, result: Any) -> MessageInfo | None:
    for extractor in EXTRACTORS:
        if target.type in extractor.TARGETS:
            return extractor.extract_sent_message(target, result)
