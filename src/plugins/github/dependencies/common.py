"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:11:56
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-29 16:15:24
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Any

from nonebot.typing import T_State
from nonebot.params import Depends, RegexDict


async def store_regex_vars(state: T_State, group: dict[str, Any] = RegexDict()):
    state.update(group)


STORE_REGEX_VARS = Depends(store_regex_vars)
"""Parameterless dependency that stores regex variables in the state."""
