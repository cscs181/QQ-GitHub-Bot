"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:45:05
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:54:15
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Callable, AsyncContextManager

from nonebot import on_command
from nonebot.log import logger
from githubkit.rest import Issue
from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.typing import T_State
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.github import GitHubBot, ActionTimeout
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.github import config
from src.plugins.github.libs.renderer import issue_to_image
from src.plugins.github.helpers import NO_GITHUB_EVENT, get_platform
from src.plugins.github.libs.message_tag import Tag, create_message_tag

from . import KEY_GITHUB_REPLY
from .dependencies import get_issue, get_context, is_github_reply

content = on_command(
    "content",
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@content.handle()
async def handle_content(
    event: Event,
    state: T_State,
    issue_: Issue = Depends(get_issue),
    context: Callable[[], AsyncContextManager[GitHubBot]] = Depends(get_context),
):
    tag: Tag = state[KEY_GITHUB_REPLY]

    try:
        async with context():
            img = await issue_to_image(issue_)
    except ActionTimeout:
        await content.finish("GitHub API 超时，请稍后再试")
    except TimeoutError:
        await content.finish("生成图片超时！请稍后再试")
    except Error:
        await content.finish("生成图片出错！请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating issue image: {e}")
        await content.finish("生成图片出错！请稍后再试")

    match get_platform(event):
        case "qq":
            result = await content.send(QQMS.image(img))
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
