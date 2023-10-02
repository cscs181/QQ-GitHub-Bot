"""
@Author         : yanyongyu
@Date           : 2022-09-30 08:59:36
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-04 15:32:18
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
from nonebot.adapters.github import OAuthBot, GitHubBot, ActionFailed, ActionTimeout

from src.plugins.github.models import User
from src.plugins.github.helpers import get_current_user, get_github_context
from src.plugins.github.libs.message_tag import (
    Tag,
    IssueTag,
    MessageInfo,
    PullRequestTag,
)

from . import KEY_GITHUB_REPLY


async def is_github_reply(state: T_State):
    return KEY_GITHUB_REPLY in state


async def is_pull_request(state: T_State):
    return KEY_GITHUB_REPLY in state and isinstance(
        state[KEY_GITHUB_REPLY], PullRequestTag
    )


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
) -> Callable[[], AsyncContextManager[GitHubBot | OAuthBot]]:
    tag: Tag = state[KEY_GITHUB_REPLY]
    return await get_github_context(tag.owner, tag.repo, matcher, user)


async def get_user(
    matcher: Matcher, user: User | None = Depends(get_current_user)
) -> User:
    if not user:
        await matcher.finish("你还没有绑定 GitHub 帐号，请私聊使用 /install 进行安装")
    return user


async def get_issue(
    matcher: Matcher,
    state: T_State,
    context: Callable[[], AsyncContextManager[GitHubBot | OAuthBot]] = Depends(
        get_context
    ),
) -> Issue:
    tag: Tag = state[KEY_GITHUB_REPLY]

    if not isinstance(tag, (IssueTag, PullRequestTag)):
        await matcher.finish()

    try:
        async with context() as bot:
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
