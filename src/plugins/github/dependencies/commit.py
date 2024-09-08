"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:16:46
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:43:07
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot import logger
from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from githubkit.versions.latest.models import Commit
from nonebot.adapters.github import ActionFailed, ActionTimeout

from .github import GITHUB_PUBLIC_CONTEXT


async def get_commit(
    event: Event, matcher: Matcher, state: T_State, context: GITHUB_PUBLIC_CONTEXT
) -> Commit:
    owner = state["owner"]
    repo = state["repo"]
    ref = state["commit"]

    # omit the reminder if the event is not to me
    should_remind = event.is_tome()

    try:
        async with context() as bot:
            resp = await bot.rest.repos.async_get_commit(
                owner=owner, repo=repo, ref=ref
            )
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试" if should_remind else None)
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(
                f"未找到仓库 {owner}/{repo} 的 {ref} 提交" if should_remind else None
            )
        elif e.response.status_code == 401:
            await matcher.finish(
                "你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新"
                if should_remind
                else None
            )
        logger.opt(exception=e).error(f"Failed while getting issue: {e}")
        await matcher.finish(
            "未知错误发生，请尝试重试或联系管理员" if should_remind else None
        )
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting issue: {e}")
        await matcher.finish(
            "未知错误发生，请尝试重试或联系管理员" if should_remind else None
        )


COMMIT: TypeAlias = Annotated[Commit, Depends(get_commit)]
"""Commit dependency.

Note that the owner, repo and commit sha must be stored in the state first.
"""
