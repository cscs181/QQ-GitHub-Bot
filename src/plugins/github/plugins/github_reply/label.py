"""
@Author         : yanyongyu
@Date           : 2022-10-21 07:56:27
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:55:01
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.typing import T_State
from nonebot import logger, on_shell_command
from nonebot.adapters import Event, MessageSegment
from nonebot.params import Depends, ShellCommandArgv
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT, get_platform
from src.plugins.github.libs.message_tag import (
    Tag,
    IssueTag,
    PullRequestTag,
    create_message_tag,
)

from . import KEY_GITHUB_REPLY
from .dependencies import get_user, is_github_reply

label = on_shell_command(
    "label",
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@label.handle()
async def handle_label(
    event: Event,
    state: T_State,
    labels: list[str | MessageSegment] = ShellCommandArgv(),
    user: User = Depends(get_user),
):
    bot = get_github_bot()
    tag: Tag = state[KEY_GITHUB_REPLY]
    labels_ = [label for label in labels if isinstance(label, str) and label]

    if not isinstance(tag, (IssueTag, PullRequestTag)):
        await label.finish()
    elif not labels_:
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
    tag = (
        PullRequestTag(
            owner=tag.owner, repo=tag.repo, number=tag.number, is_receive=False
        )
        if isinstance(tag, PullRequestTag)
        else IssueTag(
            owner=tag.owner, repo=tag.repo, number=tag.number, is_receive=False
        )
    )
    match get_platform(event):
        case "qq":
            result = await label.send(message)
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
