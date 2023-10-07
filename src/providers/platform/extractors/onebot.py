"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:20:11
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 17:20:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any
from typing_extensions import override

import nonebot
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)

from src.providers.platform.typing import TargetType
from src.providers.platform.targets import QQUserInfo, TargetInfo, QQGroupInfo
from src.providers.platform.messages import QQUserMessageInfo, QQGroupMessageInfo

from ._base import Extractor


class OneBotExtractor(
    Extractor[
        MessageEvent,
        GroupMessageEvent,
        MessageEvent,
    ]
):
    TARGETS = (TargetType.QQ_USER, TargetType.QQ_GROUP)

    USER_EVENTS = (MessageEvent,)
    GROUP_EVENTS = (GroupMessageEvent,)
    MESSAGE_EVENTS = (MessageEvent,)

    @classmethod
    @override
    def extract_user(cls, event) -> QQUserInfo:
        return QQUserInfo(type=TargetType.QQ_USER, qq_user_id=event.user_id)

    @classmethod
    @override
    def extract_group(cls, event) -> QQGroupInfo:
        return QQGroupInfo(type=TargetType.QQ_GROUP, qq_group_id=event.group_id)

    @classmethod
    @override
    def extract_target(cls, event) -> TargetInfo:
        return (
            QQGroupInfo(type=TargetType.QQ_GROUP, qq_group_id=event.group_id)
            if isinstance(event, GroupMessageEvent)
            else QQUserInfo(type=TargetType.QQ_USER, qq_user_id=event.user_id)
        )

    @classmethod
    @override
    def extract_is_private(cls, event) -> bool:
        return isinstance(event, PrivateMessageEvent)

    @classmethod
    @override
    def extract_message(cls, event) -> QQUserMessageInfo | QQGroupMessageInfo:
        if cls.extract_is_private(event):
            return QQUserMessageInfo(type=TargetType.QQ_USER, id=event.message_id)
        else:
            return QQGroupMessageInfo(type=TargetType.QQ_GROUP, id=event.message_id)

    @classmethod
    @override
    def get_target_bot(cls, target: TargetInfo) -> Bot:
        return next(bot for bot in nonebot.get_bots().values() if isinstance(bot, Bot))

    @classmethod
    @override
    def extract_sent_message(
        cls, target: QQUserInfo | QQGroupInfo, result: Any
    ) -> QQUserMessageInfo | QQGroupMessageInfo | None:
        if isinstance(result, dict) and "message_id" in result:
            if isinstance(target, QQUserInfo):
                return QQUserMessageInfo(type=target.type, id=result["message_id"])
            else:
                return QQGroupMessageInfo(type=target.type, id=result["message_id"])
