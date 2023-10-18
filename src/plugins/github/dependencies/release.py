"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:16:46
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 17:28:31
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot import logger
from githubkit.rest import Release
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.github import ActionFailed, ActionTimeout

from .github import GITHUB_PUBLIC_CONTEXT


async def get_release(
    matcher: Matcher, state: T_State, context: GITHUB_PUBLIC_CONTEXT
) -> Release:
    owner = state["owner"]
    repo = state["repo"]
    tag = state["tag"]

    try:
        async with context as bot:
            resp = await bot.rest.repos.async_get_release_by_tag(
                owner=owner, repo=repo, tag=tag
            )
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(f"未找到 {owner}/{repo} 的 {tag} 发布")
        elif e.response.status_code == 401:
            await matcher.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
        logger.opt(exception=e).error(f"Failed while getting issue: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting issue: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


RELEASE: TypeAlias = Annotated[Release, Depends(get_release)]
"""Release dependency.

Note that the owner, repo and tag must be stored in the state first.
"""
