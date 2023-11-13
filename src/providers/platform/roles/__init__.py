"""
@Author         : yanyongyu
@Date           : 2023-11-11 14:10:58
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-13 15:51:02
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"


from enum import IntEnum


class RoleLevel(IntEnum):
    """Role level"""

    OWNER = 40
    ADMIN = 30
    MEMBER = 20
    GUEST = 10
    UNKNOWN = 0
