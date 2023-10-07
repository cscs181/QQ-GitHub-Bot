"""
@Author         : yanyongyu
@Date           : 2022-10-18 03:18:14
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-05 20:30:28
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot import logger, on_command
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.providers.platform import PLATFORM, MESSAGE_INFO, extract_sent_message
from src.plugins.github.cache.message_tag import Tag, RepoTag, create_message_tag

from . import KEY_GITHUB_REPLY
from .dependencies import get_user, is_github_reply

unstar = on_command(
    "unstar",
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@unstar.handle()
async def handle_unstar(
    event: Event,
    state: T_State,
    platform: PLATFORM,
    message_info: MESSAGE_INFO,
    user: User = Depends(get_user),
):
    bot = get_github_bot()
    tag: Tag = state[KEY_GITHUB_REPLY]

    if message_info:
        await create_message_tag(
            message_info,
            tag.copy(update={"is_receive": True}),
        )

    async with bot.as_user(user.access_token):
        # check starred
        message: str | None = None
        try:
            await bot.rest.activity.async_check_repo_is_starred_by_authenticated_user(
                owner=tag.owner, repo=tag.repo
            )
        except ActionTimeout:
            await unstar.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code == 401:
                await unstar.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
            elif e.response.status_code == 403:
                await unstar.finish("权限不足，请尝试使用 /auth 刷新授权")
            elif e.response.status_code != 404:
                logger.opt(exception=e).error(
                    f"Failed while checking repo in unstar: {e}"
                )
                await unstar.finish("未知错误发生，请尝试重试或联系管理员")
            message = f"你还没有为 {tag.owner}/{tag.repo} 点过 star"
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while checking repo in unstar: {e}")
            await unstar.finish("未知错误发生，请尝试重试或联系管理员")

        if message is None:
            try:
                await bot.rest.activity.async_unstar_repo_for_authenticated_user(
                    owner=tag.owner, repo=tag.repo
                )
                message = f"成功为 {tag.owner}/{tag.repo} 取消 star"
            except ActionTimeout:
                await unstar.finish("GitHub API 超时，请稍后再试")
            except ActionFailed as e:
                if e.response.status_code == 403:
                    await unstar.finish(f"权限不足，{tag.owner}/{tag.repo} 未安装 APP")
                elif e.response.status_code == 404:
                    await unstar.finish(f"仓库 {tag.owner}/{tag.repo} 不存在")
                logger.opt(exception=e).error(
                    f"Failed while checking repo in unstar: {e}"
                )
                await unstar.finish("未知错误发生，请尝试重试或联系管理员")
            except Exception as e:
                logger.opt(exception=e).error(
                    f"Failed while checking repo in unstar: {e}"
                )
                await unstar.finish("未知错误发生，请尝试重试或联系管理员")

    match platform:
        case "qq":
            result = await unstar.send(message)
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
            return

    tag = RepoTag(owner=tag.owner, repo=tag.repo, is_receive=False)
    if sent_message_info := extract_sent_message(platform, result):
        await create_message_tag(sent_message_info, tag)
