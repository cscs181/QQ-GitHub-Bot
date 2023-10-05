from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, TypeAlias

from src.providers.platform.typing import PLATFORMS

from ._base import Entity

P = TypeVar("P", bound=PLATFORMS)
GID = TypeVar("GID", int, str)
CID = TypeVar("CID", int, str)


@dataclass(frozen=True, slots=True)
class BaseChannel(Entity, Generic[P, GID, CID]):
    """Channel entity that can be identified by guild and channel id."""

    platform: P
    guild_id: GID
    id: CID


ChannelInt: TypeAlias = BaseChannel[P, int, int]
ChannelStr: TypeAlias = BaseChannel[P, str, str]

QQGuildChannel: TypeAlias = ChannelStr[Literal["qqguild"]]

Channel: TypeAlias = QQGuildChannel
