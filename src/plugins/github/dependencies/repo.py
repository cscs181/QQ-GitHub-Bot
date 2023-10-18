"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:16:55
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-07 17:17:00
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from githubkit.rest import FullRepository
from nonebot.adapters.github import ActionFailed, ActionTimeout

from .github import GITHUB_PUBLIC_CONTEXT


async def get_repo(
    matcher: Matcher, state: T_State, context: GITHUB_PUBLIC_CONTEXT
) -> FullRepository:
    owner = state["owner"]
    repo = state["repo"]

    try:
        async with context as bot:
            resp = await bot.rest.repos.async_get(owner=owner, repo=repo)
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(f"未找到仓库 {owner}/{repo}")
        elif e.response.status_code == 401:
            await matcher.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
        logger.opt(exception=e).error(f"Failed while getting repo: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting repo: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


REPOSITORY: TypeAlias = Annotated[FullRepository, Depends(get_repo)]
"""Repository dependency.

Note that the owner and repo must be stored in the state first.
"""
