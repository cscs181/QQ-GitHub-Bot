"""
@Author         : yanyongyu
@Date           : 2023-03-04 17:55:56
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-05 20:01:47
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import T_State
from nonebot import logger, on_command
from nonebot.adapters import Event, Message
from nonebot.params import Depends, CommandArg
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.providers.platform import PLATFORM, MESSAGE_INFO, extract_sent_message
from src.plugins.github.cache.message_tag import (
    Tag,
    IssueTag,
    PullRequestTag,
    create_message_tag,
)

from . import KEY_GITHUB_REPLY
from .dependencies import get_user, is_github_reply

comment = on_command(
    "comment",
    aliases={"reply"},
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@comment.handle()
async def handle_comment(
    event: Event,
    state: T_State,
    platform: PLATFORM,
    message_info: MESSAGE_INFO,
    content: Message = CommandArg(),
    user: User = Depends(get_user),
):
    bot = get_github_bot()
    tag: Tag = state[KEY_GITHUB_REPLY]

    if not isinstance(tag, (IssueTag, PullRequestTag)):
        await comment.finish()

    if message_info:
        await create_message_tag(
            message_info,
            tag.copy(update={"is_receive": True}),
        )

    if not (body := content.extract_plain_text()):
        await comment.finish("评论内容不能为空")

    try:
        async with bot.as_user(user.access_token):
            await bot.rest.issues.async_create_comment(
                owner=tag.owner,
                repo=tag.repo,
                issue_number=tag.number,
                body=body,
            )
    except ActionTimeout:
        await comment.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await comment.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        logger.opt(exception=e).error(f"Failed while comment issue: {e}")
        await comment.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while comment issue: {e}")
        await comment.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功评论 {tag.owner}/{tag.repo}#{tag.number}"
    match platform:
        case "qq":
            result = await comment.send(message)
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
            return

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(platform, result):
        await create_message_tag(sent_message_info, tag)
