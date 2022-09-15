#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:09:04
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-15 17:37:50
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from unidiff import PatchSet
from githubkit.rest import Issue, PullRequest, FullRepository

from src.plugins.github.utils import get_bot


async def get_issue_repo(issue: Issue) -> FullRepository:
    bot = get_bot()
    resp = await bot.github.arequest(
        "GET", issue.repository_url, response_model=FullRepository
    )
    return resp.parsed_data


def get_issue_timeline(owner: str, repo: str, issue: Issue):
    bot = get_bot()
    return bot.github.paginate(
        bot.rest.issues.async_list_events_for_timeline,
        owner=owner,
        repo=repo,
        issue_number=issue.number,
    )


async def get_pull_request(owner: str, repo: str, issue: Issue) -> PullRequest:
    bot = get_bot()
    resp = await bot.rest.pulls.async_get(
        owner=owner, repo=repo, pull_number=issue.number
    )
    return resp.parsed_data


async def get_pull_request_diff(pr: PullRequest) -> PatchSet:
    bot = get_bot()
    resp = await bot.github.arequest("GET", pr.diff_url)
    return PatchSet.from_string(resp.text)
