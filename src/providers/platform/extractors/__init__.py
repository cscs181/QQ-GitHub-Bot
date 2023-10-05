from typing import Any, cast

from nonebot.adapters import Event

from src.providers.platform.typing import PLATFORMS
from src.providers.platform.entities import User, Group, Channel, Message

from ._base import Extractor as Extractor
from .onebot import OneBotExtractor as OneBotExtractor

EXTRACTORS = cast(tuple[type[Extractor], ...], (OneBotExtractor,))


def extract_platform(event: Event) -> PLATFORMS | None:
    for extractor in EXTRACTORS:
        if isinstance(
            event,
            extractor.USER_EVENTS + extractor.GROUP_EVENTS + extractor.CHANNEL_EVENTS,
        ):
            return extractor.extract_platform(event)


def extract_user(event: Event) -> User | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.USER_EVENTS):
            return extractor.extract_user(event)


def extract_group(event: Event) -> Group | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.GROUP_EVENTS):
            return extractor.extract_group(event)


def extract_channel(event: Event) -> Channel | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.CHANNEL_EVENTS):
            return extractor.extract_channel(event)


def extract_is_private(event: Event) -> bool | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.PRIVATE_EVENTS):
            return extractor.extract_is_private(event)


def extract_message(event: Event) -> Message | None:
    for extractor in EXTRACTORS:
        if isinstance(event, extractor.MESSAGE_EVENTS):
            return extractor.extract_message(event)


def extract_sent_message(platform: PLATFORMS, result: Any) -> Message | None:
    for extractor in EXTRACTORS:
        if platform in extractor.PLATFORMS:
            return extractor.extract_sent_message(result)
