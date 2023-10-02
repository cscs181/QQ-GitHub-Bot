"""
@Author         : yanyongyu
@Date           : 2022-09-12 08:56:39
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 23:22:27
@Description    : Permission helpers
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import PRIVATE, GROUP_ADMIN, GROUP_OWNER

PRIVATE_PERM = PRIVATE
"""All platform private permission"""

GROUP_SUPERPERM = SUPERUSER | GROUP_OWNER | GROUP_ADMIN
"""All platform group admin or superuser permission"""
