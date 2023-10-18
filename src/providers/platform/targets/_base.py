"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:19:08
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 17:19:08
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from pydantic import BaseModel

from src.providers.platform.typing import TargetType


class BaseTargetInfo(BaseModel):
    type: TargetType
