#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-30 08:59:36
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-05 08:30:55
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Callable, AsyncContextManager

from nonebot.log import logger
from githubkit.rest import Issue
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.github import GitHubBot, ActionFailed, ActionTimeout

from src.plugins.github.models import User
from src.plugins.github.utils import get_bot
from src.plugins.github.helpers import get_current_user, get_github_context
from src.plugins.github.libs.message_tag import (
    Tag,
    IssueTag,
    MessageInfo,
    PullRequestTag,
)

from . import KEY_GITHUB_REPLY


async def get_qq_reply(event: MessageEvent) -> MessageInfo | None:
    if event.reply:
        return {"type": "qq", "message_id": str(event.reply.message_id)}


async def get_reply(
    qq_info: MessageInfo | None = Depends(get_qq_reply),
    # qqguild_info: MessageInfo | None = Depends(get_qqguild_reply),
) -> MessageInfo | None:
    return qq_info


async def get_context(
    matcher: Matcher,
    state: T_State,
    user: User | None = Depends(get_current_user),
) -> Callable[[], AsyncContextManager[GitHubBot]]:
    tag: Tag = state[KEY_GITHUB_REPLY]
    return await get_github_context(tag.owner, tag.repo, matcher, user)


async def get_issue(
    matcher: Matcher,
    state: T_State,
    context: Callable[[], AsyncContextManager[GitHubBot]] = Depends(get_context),
) -> Issue:
    bot = get_bot()
    tag: Tag = state[KEY_GITHUB_REPLY]

    if not isinstance(tag, (IssueTag, PullRequestTag)):
        await matcher.finish()

    try:
        async with context():
            resp = await bot.rest.issues.async_get(
                owner=tag.owner, repo=tag.repo, issue_number=tag.number
            )
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(
                f"未找到 {tag.owner}/{tag.repo}#{tag.number} 对应的 Issue 或 PR"
            )
        logger.opt(exception=e).error(f"Failed while checking repo in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while checking repo in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
