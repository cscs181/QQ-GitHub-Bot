"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:19:08
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-11 14:58:02
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from enum import Enum

from pydantic import BaseModel


class TargetType(str, Enum):
    # User
    QQ_USER = "qq_user"
    QQ_OFFICIAL_USER = "qq_official_user"
    QQGUILD_USER = "qqguild_user"

    # Group
    QQ_GROUP = "qq_group"
    QQ_OFFICIAL_GROUP = "qq_official_group"
    QQGUILD_CHANNEL = "qqguild_channel"


class BaseTargetInfo(BaseModel):
    type: TargetType
