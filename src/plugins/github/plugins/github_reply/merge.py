"""
@Author         : yanyongyu
@Date           : 2023-04-04 18:54:22
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 15:44:16
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from githubkit.utils import UNSET
from nonebot.adapters import Message
from nonebot import logger, on_command
from nonebot.exception import MatcherException
from nonebot.params import Command, CommandArg
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import REPLY_PR, NO_GITHUB_EVENT
from src.plugins.github.cache.message_tag import create_message_tag
from src.plugins.github.dependencies import PR_REPLY_TAG, AUTHORIZED_USER
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

merge = on_command(
    "merge",
    aliases={"squash", "rebase"},
    rule=NO_GITHUB_EVENT & REPLY_PR,
    priority=config.github_command_priority,
    block=True,
)


@merge.handle()
async def handle_merge(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    user: AUTHORIZED_USER,
    tag: PR_REPLY_TAG,
    action: tuple[str, ...] = Command(),
    content: Message = CommandArg(),
):
    bot = get_github_bot()

    if action[0] not in ("merge", "squash", "rebase"):
        await merge.finish(f"操作 {action[0]} 不允许")

    await create_message_tag(
        message_info,
        tag.copy(update={"is_receive": True}),
    )

    async with bot.as_user(user.access_token):
        try:
            pull_request = await bot.rest.pulls.async_get(
                owner=tag.owner, repo=tag.repo, pull_number=tag.number
            )
            mergeable = pull_request.parsed_data.mergeable
        except ActionTimeout:
            await merge.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code == 404:
                await merge.finish(
                    f"未找到 {tag.owner}/{tag.repo}#{tag.number} 对应的 PR"
                )
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")

        if mergeable is None:
            await merge.finish("GitHub 正在检查 PR 是否可合并，请稍后再试")
        elif mergeable is not True:
            await merge.finish("PR 当前无法合并")

        try:
            await bot.rest.pulls.async_check_if_merged(
                owner=tag.owner, repo=tag.repo, pull_number=tag.number
            )
            await merge.finish(f"PR {tag.owner}/{tag.repo}#{tag.number} 已经合并")
        except MatcherException:
            raise
        except ActionTimeout:
            await merge.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code != 404:
                logger.opt(exception=e).error(f"Failed while merge pr: {e}")
                await merge.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")

        try:
            await bot.rest.pulls.async_merge(
                owner=tag.owner,
                repo=tag.repo,
                pull_number=tag.number,
                merge_method=action[0],
                commit_title=content.extract_plain_text().strip() or UNSET,
            )
        except ActionTimeout:
            await merge.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code == 403:
                await merge.finish("权限不足，请尝试使用 /install 安装或刷新授权")
            elif e.response.status_code == 404:
                await merge.finish(
                    f"未找到 {tag.owner}/{tag.repo}#{tag.number} 对应的 PR"
                )
            elif e.response.status_code == 405:
                await merge.finish(
                    f"合并 {tag.owner}/{tag.repo}#{tag.number} 请求不允许"
                )
            # status code 409 not processed
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功合并了 PR {tag.owner}/{tag.repo}#{tag.number}"
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await merge.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await merge.send(message)

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
