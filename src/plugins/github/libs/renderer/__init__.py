#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : yanyongyu
@LastEditTime   : 2023-04-05 01:04:33
@Description    : GitHub image renderer
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import timedelta

from githubkit import rest, webhooks

from src.plugins.github import config
from src.providers.redis import cache
from src.providers.playwright import get_new_page

from .render import issue_to_html, pr_diff_to_html, issue_opened_to_html


@cache(ex=timedelta(minutes=30))
async def _gen_image(html: str, width: int, height: int) -> bytes:
    async with get_new_page(viewport={"width": width, "height": height}) as page:
        await page.set_content(html)
        return await page.screenshot(timeout=60_000, full_page=True)


async def issue_to_image(
    issue: rest.Issue,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github issue/pr timeline to image"""
    html = await issue_to_html(issue, config.github_theme)
    return await _gen_image(html, width, height)


async def pr_diff_to_image(
    issue: rest.Issue,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github pr diff to image"""
    html = await pr_diff_to_html(issue, config.github_theme)
    return await _gen_image(html, width, height)


async def issue_opened_to_image(
    repo: webhooks.Repository,
    issue: webhooks.IssuesOpenedPropIssue | webhooks.PullRequestOpenedPropPullRequest,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render webhook event issue/opened to image"""
    html = await issue_opened_to_html(repo, issue, config.github_theme)
    return await _gen_image(html, width, height)
