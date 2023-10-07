"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:20:01
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 17:20:01
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import abc
from typing import Any, Generic, TypeVar

from nonebot.adapters import Bot, Event

from src.providers.platform.typing import TargetType
from src.providers.platform.messages import MessageInfo
from src.providers.platform.targets import UserInfo, GroupInfo, TargetInfo

UE = TypeVar("UE", bound=Event)
GE = TypeVar("GE", bound=Event)
ME = TypeVar("ME", bound=Event)


class Extractor(abc.ABC, Generic[UE, GE, ME]):
    TARGETS: tuple[TargetType, ...]
    """Targets that can be extracted from the event or api result"""

    USER_EVENTS: tuple[type[UE], ...]
    """Events that are related to users"""
    GROUP_EVENTS: tuple[type[GE], ...]
    """Events that are related to groups"""
    MESSAGE_EVENTS: tuple[type[ME], ...]
    """Events that have messages"""

    @classmethod
    @abc.abstractmethod
    def extract_user(cls, event: UE) -> UserInfo:
        """Get the user from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_group(cls, event: GE) -> GroupInfo:
        """Get the group from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_target(cls, event: UE | GE) -> TargetInfo:
        """Get the target from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_is_private(cls, event: UE) -> bool:
        """Get whether the event is private"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_message(cls, event: ME) -> MessageInfo:
        """Get the message from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_target_bot(cls, target: TargetInfo) -> Bot:
        """Get the bot for the target"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_sent_message(
        cls, target: TargetInfo, result: Any
    ) -> MessageInfo | None:
        """Get the message from the result of sending a message"""
        raise NotImplementedError
