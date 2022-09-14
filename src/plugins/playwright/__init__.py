#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 14:22:39
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 15:03:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from nonebot import get_driver
from playwright.async_api import Page, Browser, Playwright, async_playwright

driver = get_driver()

_playwright: Playwright | None = None
_browser: Browser | None = None


@driver.on_startup
async def start_browser():
    global _playwright
    global _browser
    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch()


@driver.on_shutdown
async def shutdown_browser():
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()


@asynccontextmanager
async def get_new_page(**kwargs) -> AsyncGenerator[Page, None]:
    assert _browser, "playwright is not initalized"
    page = await _browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()
