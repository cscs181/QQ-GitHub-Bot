"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:11:56
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 17:13:38
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import T_State
from nonebot.params import Depends, RegexDict


async def store_regex_vars(state: T_State, group: dict[str, str] = RegexDict()):
    state.update(group)


STORE_REGEX_VARS = Depends(store_regex_vars)
"""Parameterless dependency that stores regex variables in the state."""
