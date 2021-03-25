#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-25 16:15:55
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path
from typing import List, Optional

import markdown

from src.libs import html2img
from src.libs.github import Github
from ... import github_config as config
from src.libs.github.models import Issue
from src.libs.playwright import get_new_page


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

    try:
        repo = await g.get_repo(f"{owner}/{repo_name}", True)
        issue = await repo.get_issue(number)
    finally:
        await g.close()
    return issue


HEADER = """
# {title} <font color=#8b949e>#{number}</font>

<span class="State State--{status}">{status}</span> <small><font color=#8b949e>{comments} comments</font></small>

### **{login}** <small><font color=#8b949e>{updated_at}</font></small>
"""
OPTIONS: dict = {"encoding": "utf-8"}
CSS_FILES: List[str] = [
    str(Path(__file__).parent / "github.css"),
    str(Path(__file__).parent / "status.css")
]


async def issue_to_image(issue: Issue,
                         width: int = 800,
                         wkhtmltoimage: bool = False) -> Optional[bytes]:
    if issue.body_html:
        html = '<article class="markdown-body">' + markdown.markdown(
            HEADER.format(
                title=issue.title,
                number=issue.number,
                status=issue.state,
                comments=issue.comments,
                login=issue.user.login,
                updated_at=issue.updated_at.strftime(
                    "%Y-%m-%d %H:%M:%S"))) + issue.body_html + "</article>"
    elif issue.body:
        html = '<article class="markdown-body">' + markdown.markdown(
            HEADER.format(title=issue.title,
                          number=issue.number,
                          status=issue.state,
                          comments=issue.comments,
                          login=issue.user.login,
                          updated_at=issue.updated_at.strftime(
                              "%Y-%m-%d %H:%M:%S")) + issue.body) + "</article>"
    else:
        html = '<article class="markdown-body">' + markdown.markdown(
            HEADER.format(title=issue.title,
                          number=issue.number,
                          status=issue.state,
                          comments=issue.comments,
                          login=issue.user.login,
                          updated_at=issue.updated_at.strftime(
                              "%Y-%m-%d %H:%M:%S")) +
            "_No description provided._\n") + "</article>"

    OPTIONS["width"] = width
    imgkit = await html2img.IMGKit(html,
                                   "string",
                                   options=OPTIONS,
                                   css=CSS_FILES)
    if not wkhtmltoimage:
        imgkit._prepend_css(CSS_FILES)
        html: str = imgkit.source.get_source()  # type: ignore
        async with get_new_page(viewport={
                "width": width,
                "height": 300
        }) as page:
            await page.set_content(html)
            img = await page.screenshot(full_page=True)
            return img
    else:
        return await imgkit.to_img()
