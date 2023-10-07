"""
@Author         : yanyongyu
@Date           : 2022-10-21 07:08:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-05 20:11:37
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
from src.plugins.github.cache.message_tag import PullRequestTag, create_message_tag

from . import KEY_GITHUB_REPLY
from .dependencies import get_user, is_pull_request

approve = on_command(
    "approve",
    rule=NO_GITHUB_EVENT & is_pull_request,
    priority=config.github_command_priority,
    block=True,
)


@approve.handle()
async def handle_approve(
    event: Event,
    state: T_State,
    platform: PLATFORM,
    message_info: MESSAGE_INFO,
    content: Message = CommandArg(),
    user: User = Depends(get_user),
):
    bot = get_github_bot()
    tag: PullRequestTag = state[KEY_GITHUB_REPLY]

    if message_info:
        await create_message_tag(
            message_info,
            tag.copy(update={"is_receive": True}),
        )

    try:
        async with bot.as_user(user.access_token):
            await bot.rest.pulls.async_create_review(
                owner=tag.owner,
                repo=tag.repo,
                pull_number=tag.number,
                event="APPROVE",
                body=content.extract_plain_text().strip() or UNSET,
            )
    except ActionTimeout:
        await approve.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await approve.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        elif e.response.status_code == 404:
            await approve.finish("批准 PR 失败，可能是因为 PR 已经被合并或关闭")
        elif e.response.status_code == 422:
            await approve.finish("批准 PR 失败，可能是因为不能批准自己的 PR")
        logger.opt(exception=e).error(f"Failed while approve pr: {e}")
        await approve.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while approve pr: {e}")
        await approve.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功批准了 PR {tag.owner}/{tag.repo}#{tag.number}"
    match platform:
        case "qq":
            result = await approve.send(message)
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
            return

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(platform, result):
        await create_message_tag(sent_message_info, tag)
