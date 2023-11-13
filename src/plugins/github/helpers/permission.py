"""
@Author         : yanyongyu
@Date           : 2022-09-12 08:56:39
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-13 17:31:20
@Description    : Permission helpers
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot.permission import SUPERUSER, Permission

from src.providers.platform import OPTIONAL_ROLE, OPTIONAL_IS_PRIVATE, RoleLevel


async def private_perm(is_private: OPTIONAL_IS_PRIVATE) -> bool:
    """Check if the event is a private message"""
    return is_private is True


PRIVATE_PERM = Permission(private_perm)
"""All platform private permission"""


async def group_superperm(role: OPTIONAL_ROLE) -> bool:
    """Check if the event is a group message and the user is superuser"""
    return role is not None and role >= RoleLevel.ADMIN


GROUP_SUPERPERM = SUPERUSER | Permission(group_superperm)
"""All platform group admin or superuser permission"""
