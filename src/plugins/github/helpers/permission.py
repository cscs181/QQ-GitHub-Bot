#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-12 08:56:39
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:42:47
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import PRIVATE, GROUP_ADMIN, GROUP_OWNER

# all platform private
PRIVATE_PERM = PRIVATE

# all platform group admin or superuser
GROUP_SUPERPERM = SUPERUSER | GROUP_OWNER | GROUP_ADMIN
