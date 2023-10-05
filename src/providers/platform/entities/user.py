from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, TypeAlias

from src.providers.platform.typing import PLATFORMS

from ._base import Entity

P = TypeVar("P", bound=PLATFORMS)
ID = TypeVar("ID", int, str)


@dataclass(frozen=True, slots=True)
class BaseUser(Entity, Generic[P, ID]):
    """User entity that can be identified by simple id."""

    platform: P
    id: ID


UserInt: TypeAlias = BaseUser[P, int]
UserStr: TypeAlias = BaseUser[P, str]

QQUser: TypeAlias = UserInt[Literal["qq"]]
QQGuildUser: TypeAlias = UserStr[Literal["qqguild"]]
QQOfficialUser: TypeAlias = UserStr[Literal["qq_official"]]

User: TypeAlias = QQUser | QQGuildUser | QQOfficialUser
