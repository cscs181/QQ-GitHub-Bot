"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:59:59
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-05 20:03:42
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Callable, AsyncContextManager

from githubkit.rest import Issue
from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot import logger, on_command
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.github import GitHubBot, ActionTimeout
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.github import config
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.libs.renderer import pr_diff_to_image
from src.providers.platform import PLATFORM, MESSAGE_INFO, extract_sent_message
from src.plugins.github.cache.message_tag import PullRequestTag, create_message_tag

from . import KEY_GITHUB_REPLY
from .dependencies import get_issue, get_context, is_pull_request

diff = on_command(
    "diff",
    rule=NO_GITHUB_EVENT & is_pull_request,
    priority=config.github_command_priority,
    block=True,
)


@diff.handle()
async def handle_diff(
    event: Event,
    state: T_State,
    platform: PLATFORM,
    message_info: MESSAGE_INFO,
    issue_: Issue = Depends(get_issue),
    context: Callable[[], AsyncContextManager[GitHubBot]] = Depends(get_context),
):
    tag: PullRequestTag = state[KEY_GITHUB_REPLY]

    if message_info:
        await create_message_tag(
            message_info,
            tag.copy(update={"is_receive": True}),
        )

    try:
        async with context():
            img = await pr_diff_to_image(issue_)
    except ActionTimeout:
        await diff.finish("GitHub API 超时，请稍后再试")
    except TimeoutError:
        await diff.finish("生成图片超时！请稍后再试")
    except Error:
        await diff.finish("生成图片出错！请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating issue image: {e}")
        await diff.finish("生成图片出错！请稍后再试")

    match platform:
        case "qq":
            result = await diff.send(QQMS.image(img))
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
            return

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(platform, result):
        await create_message_tag(sent_message_info, tag)
