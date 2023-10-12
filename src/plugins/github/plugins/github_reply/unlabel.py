"""
@Author         : yanyongyu
@Date           : 2022-10-21 08:13:17
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 16:00:03
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import logger, on_command
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

unlabel = on_command(
    "unlabel",
    rule=NO_GITHUB_EVENT & REPLY_ISSUE_OR_PR,
    priority=config.github_command_priority,
    block=True,
)


@unlabel.handle()
async def handle_unlabel(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    user: AUTHORIZED_USER,
    tag: ISSUE_OR_PR_REPLY_TAG,
    label: Message = CommandArg(),
):
    bot = get_github_bot()
    label_ = label.extract_plain_text()

    await create_message_tag(
        message_info,
        tag.copy(update={"is_receive": True}),
    )

    if not label_:
        await unlabel.finish("标签名不能为空")

    try:
        async with bot.as_user(user.access_token):
            await bot.rest.issues.async_remove_label(
                owner=tag.owner,
                repo=tag.repo,
                issue_number=tag.number,
                name=label_,
            )
    except ActionTimeout:
        await unlabel.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await unlabel.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        elif e.response.status_code == 404:
            await unlabel.finish(
                f"{tag.owner}/{tag.repo}#{tag.number} 不存在标签 {label_}"
            )
        logger.opt(exception=e).error(f"Failed while unlabel issue: {e}")
        await unlabel.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while unlabel issue: {e}")
        await unlabel.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功为 {tag.owner}/{tag.repo}#{tag.number} 移除了标签 {label_}"
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await unlabel.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await unlabel.send(message)

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
