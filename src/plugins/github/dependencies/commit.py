"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:16:46
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 17:26:36
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot import logger
from githubkit.rest import Commit
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.github import ActionFailed, ActionTimeout

from .github import GITHUB_PUBLIC_CONTEXT


async def get_commit(
    matcher: Matcher, state: T_State, context: GITHUB_PUBLIC_CONTEXT
) -> Commit:
    owner = state["owner"]
    repo = state["repo"]
    ref = state["commit"]

    try:
        async with context as bot:
            resp = await bot.rest.repos.async_get_commit(
                owner=owner, repo=repo, ref=ref
            )
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(f"未找到 {owner}/{repo} 的 {ref} 提交")
        elif e.response.status_code == 401:
            await matcher.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
        logger.opt(exception=e).error(f"Failed while getting issue: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting issue: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


COMMIT: TypeAlias = Annotated[Commit, Depends(get_commit)]
"""Commit dependency.

Note that the owner, repo and commit sha must be stored in the state first.
"""
