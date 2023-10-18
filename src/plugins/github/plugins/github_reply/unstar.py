"""
@Author         : yanyongyu
@Date           : 2022-10-18 03:18:14
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 16:02:40
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot import logger, on_command
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import REPLY_ANY, NO_GITHUB_EVENT
from src.plugins.github.dependencies import REPLY_TAG, AUTHORIZED_USER
from src.plugins.github.cache.message_tag import RepoTag, create_message_tag
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

unstar = on_command(
    "unstar",
    rule=NO_GITHUB_EVENT & REPLY_ANY,
    priority=config.github_command_priority,
    block=True,
)


@unstar.handle()
async def handle_unstar(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    tag: REPLY_TAG,
    user: AUTHORIZED_USER,
):
    bot = get_github_bot()

    await create_message_tag(
        message_info, RepoTag(owner=tag.owner, repo=tag.repo, is_receive=True)
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

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await unstar.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await unstar.send(message)

    tag = RepoTag(owner=tag.owner, repo=tag.repo, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
