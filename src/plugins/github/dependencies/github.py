"""
@Author         : yanyongyu
@Date           : 2023-10-07 17:16:28
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:53:02
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated
from functools import partial
from collections.abc import Callable, AsyncGenerator
from contextlib import nullcontext, asynccontextmanager, _AsyncGeneratorContextManager

from nonebot import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.github import OAuthBot, GitHubBot, ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.utils import get_oauth_bot, get_github_bot

from .user import USER


@asynccontextmanager
async def github_installation_context(
    installation_id: int,
) -> AsyncGenerator[GitHubBot, None]:
    bot = get_github_bot()

    async with bot.as_installation(installation_id):
        yield bot


@asynccontextmanager
async def github_user_context(token: str) -> AsyncGenerator[GitHubBot, None]:
    bot = get_github_bot()

    async with bot.as_user(token):
        yield bot


async def get_github_public_context(
    matcher: Matcher, state: T_State, user: USER
) -> Callable[[], _AsyncGeneratorContextManager[GitHubBot] | nullcontext[OAuthBot]]:
    """Get current GitHub public context from event user.

    Return a callable to make sure the context can be reused in dependency cache.
    """

    bot = get_github_bot()

    # First use user auth, allow user to access private repo if authorized
    if user and user.access_token is not None:
        try:
            async with bot.as_oauth_app():
                resp = await bot.rest.apps.async_check_token(
                    client_id=config.github_app.client_id,
                    access_token=user.access_token,
                )
                return partial(github_user_context, user.access_token)
        except ActionTimeout:
            await matcher.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code != 404:
                logger.opt(exception=e).error(
                    f"Failed while checking token in context: {e}"
                )
                await matcher.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed while checking token in context: {e}"
            )
            await matcher.finish("未知错误发生，请尝试重试或联系管理员")

    owner = state.get("owner")
    repo = state.get("repo")

    # Second use installation
    # get repo info from state
    # since user is not authorized, only get if repo is public
    if owner is not None and repo is not None:
        try:
            resp = await bot.rest.apps.async_get_repo_installation(
                owner=owner, repo=repo
            )
            installation_id = resp.parsed_data.id
            async with bot.as_installation(installation_id):
                resp = await bot.rest.repos.async_get(owner=owner, repo=repo)
            if not resp.parsed_data.private:
                return partial(github_installation_context, installation_id)
        except ActionTimeout:
            await matcher.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code != 404:
                logger.opt(exception=e).error(
                    f"Failed while checking repo in context: {e}"
                )
                await matcher.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while checking repo in context: {e}")
            await matcher.finish("未知错误发生，请尝试重试或联系管理员")

    # Finally use oauth bot if available
    if config.oauth_app:
        return partial(nullcontext, get_oauth_bot())

    # no bot available, prompt user to install
    await matcher.finish("你还没有绑定 GitHub 帐号，请私聊使用 /install 进行安装")


GITHUB_PUBLIC_CONTEXT = Annotated[
    Callable[[], _AsyncGeneratorContextManager[GitHubBot] | nullcontext[OAuthBot]],
    Depends(get_github_public_context),
]
"""Current GitHub bot context from event.

Finish the session if no backport available.

Note that the installation context needs owner and repo info from state.
"""
