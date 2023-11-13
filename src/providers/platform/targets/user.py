"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:19:21
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-11 14:58:53
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import abc
from typing import Literal, Annotated, TypeAlias

from pydantic import Field

from ._base import TargetType, BaseTargetInfo


class BaseUserInfo(abc.ABC, BaseTargetInfo):
    """User entity."""

    type: Literal[
        TargetType.QQ_USER, TargetType.QQ_OFFICIAL_USER, TargetType.QQGUILD_USER
    ]

    @property
    @abc.abstractmethod
    def user_id(self) -> str:
        """User id to show"""
        raise NotImplementedError


class QQUserInfo(BaseUserInfo):
    """QQ user entity."""

    type: Literal[TargetType.QQ_USER]
    qq_user_id: int

    @property
    def user_id(self) -> str:
        return str(self.qq_user_id)


class QQOfficialUserInfo(BaseUserInfo):
    """QQ official user entity."""

    type: Literal[TargetType.QQ_OFFICIAL_USER]
    qq_user_open_id: str

    @property
    def user_id(self) -> str:
        return self.qq_user_open_id


class QQGuildUserInfo(BaseUserInfo):
    """QQ guild user entity."""

    type: Literal[TargetType.QQGUILD_USER]
    qqguild_user_id: str

    @property
    def user_id(self) -> str:
        return self.qqguild_user_id


UserInfo: TypeAlias = Annotated[
    QQUserInfo | QQOfficialUserInfo | QQGuildUserInfo, Field(discriminator="type")
]
