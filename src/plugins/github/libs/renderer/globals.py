#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:09:04
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-16 13:14:48
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import timedelta

from unidiff import PatchSet
from githubkit.rest import Issue, PullRequest, FullRepository

from src.plugins.redis import cache
from src.plugins.github.utils import get_bot


@cache(ex=timedelta(minutes=5))
async def get_issue_repo(issue: Issue) -> FullRepository:
    bot = get_bot()
    resp = await bot.github.arequest(
        "GET", issue.repository_url, response_model=FullRepository
    )
    return resp.parsed_data


@cache(ex=timedelta(minutes=5))
async def get_issue_timeline(owner: str, repo: str, issue: Issue):
    bot = get_bot()
    return bot.github.paginate(
        bot.rest.issues.async_list_events_for_timeline,
        owner=owner,
        repo=repo,
        issue_number=issue.number,
    )


@cache(ex=timedelta(minutes=5))
async def get_pull_request(issue: Issue) -> PullRequest:
    bot = get_bot()
    repo = await get_issue_repo(issue)
    resp = await bot.rest.pulls.async_get(
        owner=repo.owner.login, repo=repo.name, pull_number=issue.number
    )
    return resp.parsed_data


@cache(ex=timedelta(minutes=5))
async def get_pull_request_diff(pr: PullRequest) -> PatchSet:
    bot = get_bot()
    resp = await bot.github.arequest("GET", pr.diff_url)
    return PatchSet.from_string(resp.text)
