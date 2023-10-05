import abc
from typing import Any, Generic, TypeVar

from nonebot.adapters import Event

from src.providers.platform.typing import PLATFORMS
from src.providers.platform.entities import User, Group, Channel, Message

P = TypeVar("P", bound=PLATFORMS)
UE = TypeVar("UE", bound=Event)
GE = TypeVar("GE", bound=Event)
CE = TypeVar("CE", bound=Event)
PE = TypeVar("PE", bound=Event)
ME = TypeVar("ME", bound=Event)


class Extractor(abc.ABC, Generic[P, UE, GE, CE, PE, ME]):
    PLATFORMS: tuple[P, ...]
    USER_EVENTS: tuple[type[UE], ...]
    """Events that are related to users"""
    GROUP_EVENTS: tuple[type[GE], ...]
    """Events that are related to groups"""
    CHANNEL_EVENTS: tuple[type[CE], ...]
    """Events that are related to channels"""
    PRIVATE_EVENTS: tuple[type[PE], ...]
    """Events that are private"""
    MESSAGE_EVENTS: tuple[type[ME], ...]
    """Events that have messages"""

    @classmethod
    @abc.abstractmethod
    def extract_platform(cls, event: UE | GE | CE | PE | ME) -> P:
        """Get the platform name from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_user(cls, event: UE) -> User:
        """Get the user from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_group(cls, event: GE) -> Group:
        """Get the group from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_channel(cls, event: CE) -> Channel:
        """Get the channel from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_is_private(cls, event: PE) -> bool:
        """Get whether the event is private"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_message(cls, event: ME) -> Message:
        """Get the message from the event"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def extract_sent_message(cls, result: Any) -> Message | None:
        """Get the message from the result of sending a message"""
        raise NotImplementedError
