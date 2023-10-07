"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:31:37
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-05 20:13:04
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Event
from nonebot.typing import T_State
from nonebot import logger, on_command

from src.plugins.github import config
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.providers.platform import PLATFORM, MESSAGE_INFO, extract_sent_message
from src.plugins.github.cache.message_tag import (
    Tag,
    IssueTag,
    CommitTag,
    PullRequestTag,
    create_message_tag,
)

from . import KEY_GITHUB_REPLY
from .dependencies import is_github_reply

link = on_command(
    "link",
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@link.handle()
async def handle_link(
    event: Event,
    state: T_State,
    platform: PLATFORM,
    message_info: MESSAGE_INFO,
):
    tag: Tag = state[KEY_GITHUB_REPLY]

    if message_info:
        await create_message_tag(
            message_info,
            tag.copy(update={"is_receive": True}),
        )

    url = f"https://github.com/{tag.owner}/{tag.repo}"
    match tag:
        case IssueTag():
            url += f"/issues/{tag.number}"
        case PullRequestTag():
            url += f"/pull/{tag.number}"
        case CommitTag():
            url += f"/commit/{tag.commit}"

    match platform:
        case "qq":
            result = await link.send(url)
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
            return

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(platform, result):
        await create_message_tag(sent_message_info, tag)
