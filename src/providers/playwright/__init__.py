"""
@Author         : yanyongyu
@Date           : 2022-09-14 14:22:39
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-23 16:55:13
@Description    : Playwright provider plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from nonebot import get_driver
from playwright.async_api import Page, Browser, Playwright, async_playwright

driver = get_driver()

_playwright: Playwright | None = None
_browser: Browser | None = None
"""Global playwright browser instance used to control multiple pages."""


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


def get_browser() -> Browser:
    """Get the global playwright browser instance."""
    if not _browser:
        raise RuntimeError("playwright is not initalized")
    return _browser


@asynccontextmanager
async def get_new_page(**kwargs) -> AsyncGenerator[Page, None]:
    """Context manager to get a new page.

    Args:
        kwargs: Keyword arguments to pass to `browser.new_context`.
    """
    ctx = await get_browser().new_context(**kwargs)
    page = await ctx.new_page()
    try:
        yield page
    finally:
        await page.close()
        await ctx.close()
