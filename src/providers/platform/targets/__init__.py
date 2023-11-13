"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:19:00
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-11 14:58:29
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from pydantic import Field

from ._base import TargetType as TargetType
from ._base import BaseTargetInfo as BaseTargetInfo

# isort: split

from .user import UserInfo as UserInfo
from .user import QQUserInfo as QQUserInfo
from .user import BaseUserInfo as BaseUserInfo
from .user import QQGuildUserInfo as QQGuildUserInfo
from .user import QQOfficialUserInfo as QQOfficialUserInfo

# isort: split

from .group import GroupInfo as GroupInfo
from .group import QQGroupInfo as QQGroupInfo
from .group import BaseGroupInfo as BaseGroupInfo
from .group import QQGuildChannelInfo as QQGuildChannelInfo
from .group import QQOfficialGroupInfo as QQOfficialGroupInfo

TargetInfo: TypeAlias = Annotated[UserInfo | GroupInfo, Field(discriminator="type")]
