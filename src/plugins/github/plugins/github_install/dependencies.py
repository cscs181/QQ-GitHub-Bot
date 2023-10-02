"""
@Author         : yanyongyu
@Date           : 2022-09-12 08:20:06
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-05 06:35:05
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.log import logger
from nonebot.params import Depends
from nonebot.matcher import Matcher
from nonebot.adapters.github import ActionFailed, ActionTimeout
from githubkit.rest import PublicUser, PrivateUser, Installation

from src.plugins.github.models import User
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import get_current_user


async def get_github_user(
    matcher: Matcher, user: User = Depends(get_current_user)
) -> PrivateUser | PublicUser:
    bot = get_github_bot()

    try:
        async with bot.as_user(user.access_token):
            resp = await bot.rest.users.async_get_authenticated()
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 401:
            await matcher.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
        logger.opt(exception=e).error(
            f"Failed while getting github user in installation check: {e}"
        )
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while getting github user in installation check: {e}"
        )
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


async def get_user_installation(
    matcher: Matcher, user: PrivateUser | PublicUser = Depends(get_github_user)
) -> Installation:
    bot = get_github_bot()

    try:
        resp = await bot.rest.apps.async_get_user_installation(username=user.login)
        return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish(f"{user.login} 没有安装 GitHub APP 集成")
        logger.opt(exception=e).error(
            f"Failed while getting installation in installation check: {e}"
        )
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while getting installation in installation check: {e}"
        )
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
