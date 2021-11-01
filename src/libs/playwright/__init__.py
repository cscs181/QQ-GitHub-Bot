#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-12 13:42:43
@LastEditors    : yanyongyu
@LastEditTime   : 2021-11-01 14:05:41
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator

from playwright.async_api import Page, Browser, async_playwright

_browser: Optional[Browser] = None


async def init(**kwargs) -> Browser:
    global _browser
    playwright = await async_playwright().start()
    _browser = await playwright.chromium.launch(**kwargs)
    return _browser


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)


@asynccontextmanager
async def get_new_page(**kwargs) -> AsyncIterator[Page]:
    browser = await get_browser()
    page = await browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()
