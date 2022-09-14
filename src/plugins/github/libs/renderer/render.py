#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-05-14 17:09:12
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 16:12:38
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path

import jinja2
from unidiff import PatchSet
from githubkit.rest import Issue

from .globals import get_issue_timeline
from .filters import review_state, relative_time, find_dismissed_review

env = jinja2.Environment(
    extensions=["jinja2.ext.loopcontrols"],
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
    enable_async=True,
)

env.filters["relative_time"] = relative_time
env.filters["review_state"] = review_state
env.filters["find_dismissed_review"] = find_dismissed_review

env.globals["get_issue_timeline"] = get_issue_timeline


async def issue_to_html(owner: str, repo_name: str, issue: Issue) -> str:
    template = env.get_template("issue.html")
    return await template.render_async(owner=owner, repo_name=repo_name, issue=issue)


async def pr_diff_to_html(owner: str, repo_name: str, issue: Issue) -> str:
    template = env.get_template("diff.html")
    async with issue:
        pull_request = await issue.get_pull_request()
        diff = await pull_request.get_diff()
        return await template.render_async(
            owner=owner,
            repo_name=repo_name,
            issue=issue,
            pull_request=pull_request,
            diff=PatchSet(diff),
        )
