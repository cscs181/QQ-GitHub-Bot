#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 03:31:15
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-05 15:57:42
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from functools import partial
from typing import Callable, AsyncContextManager

from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.github import GitHubBot, ActionFailed, ActionTimeout

from src.plugins.github.models import User
from src.plugins.github.utils import get_github_bot

OWNER_REGEX = r"(?P<owner>[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)"
REPO_REGEX = r"(?P<repo>[a-zA-Z0-9_\-\.]+)"
FULLREPO_REGEX = rf"{OWNER_REGEX}/{REPO_REGEX}"
COMMIT_HASH_REGEX = r"(?P<commit>[0-9a-f]{5,40})"
ISSUE_REGEX = r"(?P<issue>\d+)"

GITHUB_LINK_REGEX = r"github\.com"
GITHUB_REPO_LINK_REGEX = rf"{GITHUB_LINK_REGEX}/{FULLREPO_REGEX}"
GITHUB_COMMIT_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/commit/{COMMIT_HASH_REGEX}"
GITHUB_ISSUE_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/issues/{ISSUE_REGEX}"
GITHUB_PR_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/pull/{ISSUE_REGEX}"
GITHUB_ISSUE_OR_PR_LINK_REGEX = (
    rf"{GITHUB_REPO_LINK_REGEX}/(?:issues|pull)/{ISSUE_REGEX}"
)
GITHUB_PR_COMMIT_LINK_REGEX = rf"{GITHUB_PR_LINK_REGEX}/commits/{COMMIT_HASH_REGEX}"
GITHUB_PR_FILE_LINK_REGEX = rf"{GITHUB_PR_LINK_REGEX}/files"
GITHUB_RELEASE_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/releases/tag/(?P<tag>[^/]+)"


async def get_github_context(
    owner: str, repo: str, matcher: Matcher, user: User | None = None
) -> Callable[[], AsyncContextManager[GitHubBot]]:
    bot = get_github_bot()

    # use user auth first
    if user:
        return partial(bot.as_user, user.access_token)

    # use installation second, only public repo
    try:
        resp = await bot.rest.apps.async_get_repo_installation(owner=owner, repo=repo)
        installation_id = resp.parsed_data.id
        async with bot.as_installation(installation_id):
            resp = await bot.rest.repos.async_get(owner=owner, repo=repo)
        if not resp.parsed_data.private:
            return partial(bot.as_installation, installation_id)
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code != 404:
            logger.opt(exception=e).error(f"Failed while checking repo in context: {e}")
            await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while checking repo in context: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")

    await matcher.finish("你还没有绑定 GitHub 帐号，请私聊使用 /install 进行安装")
