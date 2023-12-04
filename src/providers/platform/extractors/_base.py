"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:20:01
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-04 17:05:25
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import abc
from typing import Any, Generic, TypeVar

from nonebot.adapters import Bot, Event

from src.providers.platform.roles import RoleLevel
from src.providers.platform.messages import MessageInfo
from src.providers.platform.targets import UserInfo, GroupInfo, TargetInfo

E = TypeVar("E", bound=Event)
T = TypeVar("T", bound=TargetInfo)


class Extractor(abc.ABC, Generic[E, T]):
    EVENTS: tuple[type[E], ...]
    """Events that can be extracted and basically include user infomation"""
    TARGETS: tuple[type[T], ...]
    """Targets that can be extracted from the event or api result"""

    @classmethod
    @abc.abstractmethod
    def extract_user(cls, event: E) -> UserInfo:
        """Get the user from the event."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_group(cls, event: E) -> GroupInfo | None:
        """Get the group from the event.

        Return `None` if the event is not a group event.
        """
        raise NotImplementedError

    @classmethod
    def extract_target(cls, event: E) -> TargetInfo:
        """Get the target from the event"""
        return (
            group
            if (group := cls.extract_group(event)) is not None
            else cls.extract_user(event)
        )

    @classmethod
    def extract_is_private(cls, event: E) -> bool:
        """Get whether the event is private"""
        return cls.extract_group(event) is None

    @classmethod
    @abc.abstractmethod
    def extract_role(cls, event: E) -> RoleLevel | None:
        """Get the role level of the user in the group.

        Return `None` if the event is not a group event.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_message(cls, event: E) -> MessageInfo | None:
        """Get the message from the event.

        Return `None` if the event is not a message event.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_reply_message(cls, event: E) -> MessageInfo | None:
        """Get the reply message from the event.

        Return `None` if the event is not a message event.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def get_target_bot(cls, target: T) -> Bot:
        """Get the bot for the target"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_sent_message(cls, target: T, result: Any) -> MessageInfo | None:
        """Get the message from the result of sending a message.

        Return `None` if the result cannot be extracted.
        """
        raise NotImplementedError
