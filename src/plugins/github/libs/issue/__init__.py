#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : yanyongyu
@LastEditTime   : 2021-06-15 22:20:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import timedelta
from typing import Dict, Optional

from nonebot import require

from src.libs import html2img
from src.libs.github import Github
from ... import github_config as config
from src.libs.github.models import Issue
from src.libs.playwright import get_new_page
from .render import issue_to_html, pr_diff_to_html

cache = require("redis_provider").cache


async def get_issue(owner: str,
                    repo_name: str,
                    number: int,
                    token: Optional[str] = None) -> Issue:
    if token:
        g = Github(token)
    elif config.github_client_id and config.github_client_secret:
        g = Github(config.github_client_id, config.github_client_secret)
    else:
        g = Github()

    async with g:
        repo = await g.get_repo(f"{owner}/{repo_name}", True)
        return await repo.get_issue(number)


OPTIONS: Dict[str, str] = {"encoding": "utf-8"}
if config.xvfb_installed:
    OPTIONS["xvfb"] = ""


@cache(ex=timedelta(minutes=30))
async def _gen_image(html: str,
                     width: int,
                     height: int,
                     wkhtmltoimage: bool = False) -> Optional[bytes]:
    if not wkhtmltoimage:
        async with get_new_page(viewport={
                "width": width,
                "height": height
        }) as page:
            await page.set_content(html)
            img = await page.screenshot(full_page=True)
            return img
    else:
        imgkit = await html2img.IMGKit(html,
                                       "string",
                                       options={
                                           **OPTIONS, "width": str(width),
                                           "height": str(height)
                                       })
        return await imgkit.to_img()


async def issue_diff_to_image(owner: str,
                              repo_name: str,
                              issue: Issue,
                              width: int = 800,
                              height: int = 300,
                              wkhtmltoimage: bool = False) -> Optional[bytes]:
    if not issue.is_pull_request:
        return

    html = await pr_diff_to_html(owner, repo_name, issue)
    return await _gen_image(html, width, height, wkhtmltoimage)


async def issue_to_image(owner: str,
                         repo_name: str,
                         issue: Issue,
                         width: int = 800,
                         height: int = 300,
                         wkhtmltoimage: bool = False) -> Optional[bytes]:
    html = await issue_to_html(owner, repo_name, issue)
    return await _gen_image(html, width, height, wkhtmltoimage)
