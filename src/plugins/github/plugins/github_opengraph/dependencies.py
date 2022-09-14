#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 04:34:39
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 10:33:09
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import TypedDict

from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Depends, RegexDict
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github.utils import get_bot


class RepoID(TypedDict):
    owner: str
    repo: str


class CommitID(RepoID):
    commit: str


async def check_repo(matcher: Matcher, group: dict[str, str] = RegexDict()) -> RepoID:
    bot = get_bot()
    owner = group["owner"]
    repo = group["repo"]

    try:
        with bot.as_oauth_app():
            await bot.rest.repos.async_get(owner=owner, repo=repo)
    except ActionTimeout:
        await matcher.finish()
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish()
        logger.opt(exception=e).error(f"Failed while checking repo in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while checking repo in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")

    return RepoID(owner=owner, repo=repo)


async def check_commit(
    matcher: Matcher,
    group: dict[str, str] = RegexDict(),
    check_repo=Depends(check_repo),
) -> CommitID:
    bot = get_bot()
    owner = group["owner"]
    repo = group["repo"]
    ref = group["commit"]

    try:
        with bot.as_oauth_app():
            resp = await bot.rest.repos.async_get_commit(
                owner=owner, repo=repo, ref=ref
            )
            ref = resp.parsed_data.sha
    except ActionTimeout:
        await matcher.finish()
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish()
        logger.opt(exception=e).error(f"Failed while checking commit in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while checking commit in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")

    return CommitID(owner=owner, repo=repo, commit=ref)
