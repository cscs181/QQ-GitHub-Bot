"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:19:14
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-11 14:58:42
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Literal, Annotated, TypeAlias

from pydantic import Field

from ._base import TargetType, BaseTargetInfo


class BaseGroupInfo(BaseTargetInfo):
    """Group entity."""

    type: Literal[
        TargetType.QQ_GROUP, TargetType.QQ_OFFICIAL_GROUP, TargetType.QQGUILD_CHANNEL
    ]


class QQGroupInfo(BaseGroupInfo):
    """QQ group entity."""

    type: Literal[TargetType.QQ_GROUP]
    qq_group_id: int


class QQOfficialGroupInfo(BaseGroupInfo):
    """QQ official group entity."""

    type: Literal[TargetType.QQ_OFFICIAL_GROUP]
    qq_group_open_id: str


class QQGuildChannelInfo(BaseGroupInfo):
    """QQ guild channel entity."""

    type: Literal[TargetType.QQGUILD_CHANNEL]
    qq_guild_id: str
    qq_channel_id: str


GroupInfo: TypeAlias = Annotated[
    QQGroupInfo | QQOfficialGroupInfo | QQGuildChannelInfo, Field(discriminator="type")
]
