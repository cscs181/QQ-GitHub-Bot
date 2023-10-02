"""
@Author         : yanyongyu
@Date           : 2022-10-21 08:13:17
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:56:49
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters import Event, Message
from nonebot.params import Depends, CommandArg
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT, get_platform, get_current_user
from src.plugins.github.libs.message_tag import (
    Tag,
    IssueTag,
    PullRequestTag,
    create_message_tag,
)

from . import KEY_GITHUB_REPLY
from .dependencies import is_github_reply

unlabel = on_command(
    "unlabel",
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@unlabel.handle()
async def handle_noauth(user: None = Depends(get_current_user)):
    await unlabel.finish("你还没有绑定 GitHub 帐号，请私聊使用 /install 进行安装")


@unlabel.handle()
async def handle_label(
    event: Event,
    state: T_State,
    label: Message = CommandArg(),
    user: User = Depends(get_current_user),
):
    bot = get_github_bot()
    tag: Tag = state[KEY_GITHUB_REPLY]
    label_ = label.extract_plain_text()

    if not isinstance(tag, (IssueTag, PullRequestTag)):
        await unlabel.finish()
    elif not label_:
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
            result = await unlabel.send(message)
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
