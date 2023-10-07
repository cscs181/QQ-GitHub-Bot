"""
@Author         : yanyongyu
@Date           : 2022-10-22 03:59:07
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-05 20:10:09
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from githubkit.utils import UNSET
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

ISSUE_CLOSE_REASON = {"completed", "not_planned", ""}

close = on_command(
    "close",
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@close.handle()
async def handle_close(
    event: Event,
    state: T_State,
    platform: PLATFORM,
    message_info: MESSAGE_INFO,
    reason: Message = CommandArg(),
    user: User = Depends(get_user),
):
    bot = get_github_bot()
    tag: Tag = state[KEY_GITHUB_REPLY]

    if not isinstance(tag, (IssueTag, PullRequestTag)):
        await close.finish()

    if message_info:
        await create_message_tag(
            message_info,
            tag.copy(update={"is_receive": True}),
        )

    try:
        async with bot.as_user(user.access_token):
            if isinstance(tag, IssueTag):
                reason_ = reason.extract_plain_text().strip()
                if reason_ not in ISSUE_CLOSE_REASON:
                    await close.finish("关闭原因必须是 completed, not_planned 或者空")
                await bot.rest.issues.async_update(
                    owner=tag.owner,
                    repo=tag.repo,
                    issue_number=tag.number,
                    state="closed",
                    state_reason=reason_ or UNSET,  # type: ignore
                )
                message = f"已关闭 Issue {tag.owner}/{tag.repo}#{tag.number}"
            elif isinstance(tag, PullRequestTag):
                await bot.rest.pulls.async_update(
                    owner=tag.owner,
                    repo=tag.repo,
                    pull_number=tag.number,
                    state="closed",
                )
                message = f"已关闭 PR {tag.owner}/{tag.repo}#{tag.number}"
    except ActionTimeout:
        await close.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await close.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        logger.opt(exception=e).error(f"Failed while close pr: {e}")
        await close.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while close pr: {e}")
        await close.finish("未知错误发生，请尝试重试或联系管理员")

    match platform:
        case "qq":
            result = await close.send(message)
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
            return

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(platform, result):
        await create_message_tag(sent_message_info, tag)
