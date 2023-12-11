"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:31:37
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 15:26:29
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot import on_command

from src.plugins.github import config
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.dependencies import REPLY_TAG, OPTIONAL_REPLY_TAG
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)
from src.plugins.github.cache.message_tag import (
    IssueTag,
    CommitTag,
    ReleaseTag,
    PullRequestTag,
    create_message_tag,
)

link = on_command(
    "link",
    aliases={"链接"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@link.handle()
async def handle_no_reply(tag: OPTIONAL_REPLY_TAG):
    if tag is None:
        await link.finish("请回复 GitHub 相关消息来获取链接")


@link.handle()
async def handle_link(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    tag: REPLY_TAG,
):
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
        case ReleaseTag():
            url += f"/releases/tag/{tag.tag}"

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await link.send(url)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await link.send(url)

    tag = tag.copy(update={"is_receive": False})
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
