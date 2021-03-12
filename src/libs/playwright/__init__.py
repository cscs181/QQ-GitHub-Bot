#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-12 13:42:43
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-12 14:00:53
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional

from playwright.async_api import async_playwright, Browser

_browser: Optional[Browser] = None


async def init(**kwargs) -> Browser:
    global _browser
    playwright = await async_playwright().start()
    _browser = await playwright.chromium.launch(**kwargs)
    return _browser


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)
