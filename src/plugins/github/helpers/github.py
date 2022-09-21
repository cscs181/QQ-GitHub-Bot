#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 03:31:15
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-21 16:35:56
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import ContextManager

from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.github import GitHubBot, ActionFailed, ActionTimeout

from src.plugins.github.models import User
from src.plugins.github.utils import get_bot

OWNER_REGEX = r"(?P<owner>[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)"
REPO_REGEX = r"(?P<repo>[a-zA-Z0-9_\-\.]+)"
FULLREPO_REGEX = rf"{OWNER_REGEX}/{REPO_REGEX}"
COMMIT_HASH_REGEX = r"(?P<commit>[0-9a-f]{5,40})"
ISSUE_REGEX = r"(?P<issue>\d+)"
PULL_REGEX = r"(?P<pull>\d+)"

GITHUB_LINK_REGEX = r"github\.com"
GITHUB_REPO_LINK_REGEX = rf"{GITHUB_LINK_REGEX}/{FULLREPO_REGEX}"
GITHUB_COMMIT_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/commit/{COMMIT_HASH_REGEX}"
GITHUB_ISSUE_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/issues/{ISSUE_REGEX}"
GITHUB_PR_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/pull/{PULL_REGEX}"
GITHUB_ISSUE_OR_PR_LINK_REGEX = (
    rf"{GITHUB_REPO_LINK_REGEX}/(?:issues|pull)/{ISSUE_REGEX}"
)
GITHUB_PR_COMMIT_LINK_REGEX = rf"{GITHUB_PR_LINK_REGEX}/commits/{COMMIT_HASH_REGEX}"


async def get_github_context(
    owner: str, repo: str, matcher: Matcher, user: User | None = None
) -> ContextManager[GitHubBot]:
    bot = get_bot()
    try:
        resp = await bot.rest.apps.async_get_repo_installation(owner=owner, repo=repo)
        return bot.as_installation(resp.parsed_data.id)
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code != 404:
            logger.opt(exception=e).error(
                f"Failed while checking repo in opengraph: {e}"
            )
            await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while checking repo in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")

    if not user:
        await matcher.finish("你还没有绑定 GitHub 帐号，请使用 /install 进行安装")
    return bot.as_user(user.access_token)
