from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, TypeAlias

from src.providers.platform.typing import PLATFORMS

from ._base import Entity

P = TypeVar("P", bound=PLATFORMS)
ID = TypeVar("ID", int, str)


@dataclass(frozen=True, slots=True)
class BaseMessage(Entity, Generic[P, ID]):
    """Message entity that can be identified by simple id."""

    platform: P
    id: ID


MessageInt: TypeAlias = BaseMessage[P, int]
MessageStr: TypeAlias = BaseMessage[P, str]

QQMessage: TypeAlias = MessageInt[Literal["qq"]]
QQGuildMessage: TypeAlias = MessageStr[Literal["qqguild"]]
QQOfficialMessage: TypeAlias = MessageStr[Literal["qq_official"]]

Message: TypeAlias = QQMessage | QQGuildMessage | QQOfficialMessage
