"""
@Author         : yanyongyu
@Date           : 2023-10-08 16:14:49
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:30:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from githubkit.versions.latest.models import Installation
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github.utils import get_github_bot

from .user import GITHUB_USER


async def get_user_installation(matcher: Matcher, user: GITHUB_USER) -> Installation:
    """Get current GitHub user installation from event.

    Finish the session if user has not installed the app or API error occurs.
    """

    bot = get_github_bot()

    try:
        resp = await bot.rest.apps.async_get_user_installation(username=user.login)
        return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(
                f"用户 {user.login} 未安装 GitHub APP！\n请私聊我并使用 /install 命令进行安装"  # noqa: E501
            )
        logger.opt(exception=e).error(f"Failed while getting user installation: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting user installation: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


GITHUB_USER_INSTALLATION: TypeAlias = Annotated[
    Installation, Depends(get_user_installation)
]
"""Current GitHub user installation from event. Finish the session if not installed."""


async def get_repo_installation(matcher: Matcher, state: T_State) -> Installation:
    """Get current GitHub repository installation from event.

    Finish the session if repository has not installed the app or API error occurs.
    """

    bot = get_github_bot()

    owner = state["owner"]
    repo = state["repo"]

    try:
        resp = await bot.rest.apps.async_get_repo_installation(owner=owner, repo=repo)
        return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(
                f"仓库 {owner}/{repo} 未安装 GitHub APP！\n"
                "请私聊我并使用 /install 命令进行安装"
            )
        logger.opt(exception=e).error(f"Failed while getting repo installation: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting repo installation: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


GITHUB_REPO_INSTALLATION: TypeAlias = Annotated[
    Installation, Depends(get_repo_installation)
]
"""Current GitHub repository installation from event.

Finish the session if not installed.
"""
