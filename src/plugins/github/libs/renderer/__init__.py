#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 20:17:44
@Description    : GitHub image renderer
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import timedelta

from githubkit.rest import Issue

from src.plugins.github import config
from src.providers.redis import cache
from src.providers.playwright import get_new_page

from .render import issue_to_html, pr_diff_to_html


@cache(ex=timedelta(minutes=30))
async def _gen_image(html: str, width: int, height: int) -> bytes:
    async with get_new_page(viewport={"width": width, "height": height}) as page:
        await page.set_content(html)
        return await page.screenshot(timeout=60_000, full_page=True)


async def issue_to_image(
    issue: Issue,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github issue/pr timeline to image"""
    html = await issue_to_html(issue, config.github_theme)
    return await _gen_image(html, width, height)


async def pr_diff_to_image(
    issue: Issue,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github pr diff to image"""
    html = await pr_diff_to_html(issue, config.github_theme)
    return await _gen_image(html, width, height)
