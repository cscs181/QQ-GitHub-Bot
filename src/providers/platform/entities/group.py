from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, TypeAlias

from src.providers.platform.typing import PLATFORMS

from ._base import Entity

P = TypeVar("P", bound=PLATFORMS)
ID = TypeVar("ID", int, str)


@dataclass(frozen=True, slots=True)
class BaseGroup(Entity, Generic[P, ID]):
    """Group entity that can be identified by simple id."""

    platform: P
    id: ID


GroupInt: TypeAlias = BaseGroup[P, int]
GroupStr: TypeAlias = BaseGroup[P, str]

QQGroup: TypeAlias = GroupInt[Literal["qq"]]
QQOfficialGroup: TypeAlias = GroupStr[Literal["qq_official"]]

Group: TypeAlias = QQGroup | QQOfficialGroup
