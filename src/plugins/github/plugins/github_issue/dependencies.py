"""
@Author         : yanyongyu
@Date           : 2022-09-21 16:26:06
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-04 15:31:02
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Callable, AsyncContextManager

from nonebot.log import logger
from githubkit.rest import Issue
from nonebot.matcher import Matcher
from nonebot.params import Depends, RegexDict
from nonebot.adapters.github import OAuthBot, GitHubBot, ActionFailed, ActionTimeout

from src.plugins.github.models import User
from src.plugins.github.helpers import get_current_user, get_github_context


async def get_context(
    matcher: Matcher,
    group: dict[str, str] = RegexDict(),
    user: User | None = Depends(get_current_user),
) -> Callable[[], AsyncContextManager[GitHubBot | OAuthBot]]:
    return await get_github_context(group["owner"], group["repo"], matcher, user)


async def get_issue(
    matcher: Matcher,
    group: dict[str, str] = RegexDict(),
    context: Callable[[], AsyncContextManager[GitHubBot | OAuthBot]] = Depends(
        get_context
    ),
) -> Issue:
    owner = group["owner"]
    repo = group["repo"]
    number = int(group["issue"])

    try:
        async with context() as bot:
            resp = await bot.rest.issues.async_get(
                owner=owner, repo=repo, issue_number=number
            )
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(f"未找到 {owner}/{repo}#{number} 对应的 Issue 或 PR")
        elif e.response.status_code == 401:
            await matcher.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
        logger.opt(exception=e).error(f"Failed while checking repo in issue: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while checking repo in issue: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
