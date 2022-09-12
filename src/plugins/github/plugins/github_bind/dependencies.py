#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-07 11:58:27
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-12 09:07:50
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.matcher import Matcher


async def bypass_update(matcher: Matcher) -> None:
    if matcher.get_arg("full_name") is not None:
        matcher.skip()
