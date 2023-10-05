from typing import Any, Literal, TypeAlias
from typing_extensions import Never, override

from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)

from src.providers.platform.entities import QQUser, QQGroup, QQMessage

from ._base import Extractor

PLATFORM = "qq"
TP: TypeAlias = Literal["qq"]


class OneBotExtractor(
    Extractor[
        TP,
        MessageEvent,
        GroupMessageEvent,
        Never,
        PrivateMessageEvent,
        MessageEvent,
    ]
):
    PLATFORMS = (PLATFORM,)
    USER_EVENTS = (MessageEvent,)
    GROUP_EVENTS = (GroupMessageEvent,)
    CHANNEL_EVENTS: tuple[Never, ...] = ()
    PRIVATE_EVENTS = (PrivateMessageEvent,)
    MESSAGE_EVENTS = (MessageEvent,)

    @classmethod
    @override
    def extract_platform(cls, event) -> TP:
        return PLATFORM

    @classmethod
    @override
    def extract_user(cls, event) -> QQUser:
        return QQUser(platform=cls.extract_platform(event), id=event.user_id)

    @classmethod
    @override
    def extract_group(cls, event) -> QQGroup:
        return QQGroup(platform=cls.extract_platform(event), id=event.group_id)

    @classmethod
    @override
    def extract_channel(cls, event: Never) -> Never:
        raise RuntimeError("OneBot does not support channels")

    @classmethod
    @override
    def extract_is_private(cls, event: PrivateMessageEvent) -> bool:
        return isinstance(event, PrivateMessageEvent)

    @classmethod
    @override
    def extract_message(cls, event: MessageEvent) -> QQMessage:
        return QQMessage(platform=cls.extract_platform(event), id=event.message_id)

    @classmethod
    @override
    def extract_sent_message(cls, result: Any) -> QQMessage | None:
        if isinstance(result, dict) and "message_id" in result:
            return QQMessage(platform=PLATFORM, id=result["message_id"])
