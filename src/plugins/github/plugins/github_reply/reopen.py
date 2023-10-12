"""
@Author         : yanyongyu
@Date           : 2022-10-22 04:23:29
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 15:49:04
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import logger, on_command
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT, REPLY_ISSUE_OR_PR
from src.plugins.github.dependencies import AUTHORIZED_USER, ISSUE_OR_PR_REPLY_TAG
from src.plugins.github.cache.message_tag import (
    IssueTag,
    PullRequestTag,
    create_message_tag,
)
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

reopen = on_command(
    "reopen",
    rule=NO_GITHUB_EVENT & REPLY_ISSUE_OR_PR,
    priority=config.github_command_priority,
    block=True,
)


@reopen.handle()
async def handle_reopen(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    user: AUTHORIZED_USER,
    tag: ISSUE_OR_PR_REPLY_TAG,
):
    bot = get_github_bot()

    await create_message_tag(
        message_info,
        tag.copy(update={"is_receive": True}),
    )

    try:
        async with bot.as_user(user.access_token):
            if isinstance(tag, IssueTag):
                await bot.rest.issues.async_update(
                    owner=tag.owner,
                    repo=tag.repo,
                    issue_number=tag.number,
                    state="open",
                    state_reason="reopened",
                )
                message = f"已重新开启 Issue {tag.owner}/{tag.repo}#{tag.number}"
            elif isinstance(tag, PullRequestTag):
                await bot.rest.pulls.async_update(
                    owner=tag.owner,
                    repo=tag.repo,
                    pull_number=tag.number,
                    state="open",
                )
                message = f"已重新开启 PR {tag.owner}/{tag.repo}#{tag.number}"
    except ActionTimeout:
        await reopen.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await reopen.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        logger.opt(exception=e).error(f"Failed while reopen issue/pr: {e}")
        await reopen.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while reopen issue/pr: {e}")
        await reopen.finish("未知错误发生，请尝试重试或联系管理员")

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await reopen.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await reopen.send(message)

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
