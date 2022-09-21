#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:09:04
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-20 16:31:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import timedelta

from unidiff import PatchSet
from githubkit.exception import RequestFailed, RequestTimeout
from nonebot.adapters.github import ActionFailed, NetworkError, ActionTimeout
from githubkit.rest import Issue, PullRequest, FullRepository, TimelineCommentEvent

from src.plugins.redis import cache
from src.plugins.github.utils import get_bot

REACTION_EMOJIS = {
    "plus_one": "👍",
    "minus_one": "👎",
    "laugh": "😄",
    "confused": "😕",
    "hooray": "🎉",
    "heart": "❤️",
    "rocket": "🚀",
    "eyes": "👀",
}


@cache(ex=timedelta(minutes=5))
async def _get_issue_repo(repo_url: str) -> FullRepository:
    bot = get_bot()
    try:
        resp = await bot.github.arequest("GET", repo_url, response_model=FullRepository)
    except RequestFailed as e:
        raise ActionFailed(e.response) from None
    except RequestTimeout as e:
        raise ActionTimeout(e.request) from None
    except Exception as e:
        raise NetworkError(f"API request failed: {e!r}") from e
    return resp.parsed_data


async def get_issue_repo(issue: Issue) -> FullRepository:
    return await _get_issue_repo(issue.repository_url)


async def get_issue_timeline(issue: Issue):
    bot = get_bot()
    repo = await get_issue_repo(issue)
    return bot.github.paginate(
        bot.rest.issues.async_list_events_for_timeline,
        owner=repo.owner.login,
        repo=repo.name,
        issue_number=issue.number,
    )


@cache(ex=timedelta(minutes=5))
async def _get_pull_request(owner: str, repo: str, number: int) -> PullRequest:
    bot = get_bot()
    resp = await bot.rest.pulls.async_get(owner=owner, repo=repo, pull_number=number)
    return resp.parsed_data


async def get_pull_request(issue: Issue) -> PullRequest:
    repo = await get_issue_repo(issue)
    return await _get_pull_request(repo.owner.login, repo.name, issue.number)


@cache(ex=timedelta(minutes=5))
async def _get_pull_request_diff(diff_url: str) -> PatchSet:
    bot = get_bot()
    try:
        resp = await bot.github.arequest("GET", diff_url)
    except RequestFailed as e:
        raise ActionFailed(e.response) from None
    except RequestTimeout as e:
        raise ActionTimeout(e.request) from None
    except Exception as e:
        raise NetworkError(f"API request failed: {e!r}") from e
    return PatchSet.from_string(resp.text)


async def get_pull_request_diff(pr: PullRequest) -> PatchSet:
    return await _get_pull_request_diff(pr.diff_url)


async def get_comment_reactions(event: TimelineCommentEvent) -> dict[str, int]:
    result: dict[str, int] = {}

    if not event.reactions:
        return result

    for reaction in (
        "plus_one",
        "minus_one",
        "laugh",
        "confused",
        "hooray",
        "heart",
        "rocket",
        "eyes",
    ):
        if count := getattr(event.reactions, reaction, None):
            result[reaction] = count
    return result
