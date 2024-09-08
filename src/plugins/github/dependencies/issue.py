"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:16:46
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:43:21
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from githubkit.versions.latest.models import Issue
from nonebot.adapters.github import ActionFailed, ActionTimeout

from .github import GITHUB_PUBLIC_CONTEXT


async def get_issue(
    matcher: Matcher, state: T_State, context: GITHUB_PUBLIC_CONTEXT
) -> Issue:
    owner = state["owner"]
    repo = state["repo"]
    number = int(state["issue"])

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
        elif e.response.status_code == 410:
            await matcher.finish(f"{owner}/{repo}#{number} 对应的 Issue 或 PR 已被删除")
        elif e.response.status_code == 401:
            await matcher.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
        logger.opt(exception=e).error(f"Failed while getting issue: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting issue: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


ISSUE: TypeAlias = Annotated[Issue, Depends(get_issue)]
"""Issue dependency.

Note that the owner, repo and issue number must be stored in the state first.
"""
