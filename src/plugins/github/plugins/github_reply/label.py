"""
@Author         : yanyongyu
@Date           : 2022-10-21 07:56:27
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 15:24:41
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot import logger, on_shell_command
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.utils import get_github_bot
from src.plugins.github.cache.message_tag import create_message_tag
from src.plugins.github.helpers import NO_GITHUB_EVENT, REPLY_ISSUE_OR_PR
from src.plugins.github.dependencies import AUTHORIZED_USER, ISSUE_OR_PR_REPLY_TAG
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

label = on_shell_command(
    "label",
    rule=NO_GITHUB_EVENT & REPLY_ISSUE_OR_PR,
    priority=config.github_command_priority,
    block=True,
)


@label.handle()
async def handle_label(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    user: AUTHORIZED_USER,
    tag: ISSUE_OR_PR_REPLY_TAG,
    labels: list[str | MessageSegment] = ShellCommandArgv(),
):
    bot = get_github_bot()
    labels_ = [label for label in labels if isinstance(label, str) and label]

    await create_message_tag(
        message_info,
        tag.copy(update={"is_receive": True}),
    )

    if not labels_:
        await label.finish("标签列表不能为空")

    try:
        async with bot.as_user(user.access_token):
            await bot.rest.issues.async_add_labels(
                owner=tag.owner,
                repo=tag.repo,
                issue_number=tag.number,
                labels=labels_,
            )
    except ActionTimeout:
        await label.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await label.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        logger.opt(exception=e).error(f"Failed while label issue: {e}")
        await label.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while label issue: {e}")
        await label.finish("未知错误发生，请尝试重试或联系管理员")

    message = (
        f"成功为 {tag.owner}/{tag.repo}#{tag.number} 添加了标签 {', '.join(labels_)}"
    )
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await label.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await label.send(message)

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
