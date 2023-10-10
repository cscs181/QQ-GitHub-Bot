"""
@Author         : yanyongyu
@Date           : 2022-10-21 01:30:44
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 16:01:44
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command

from src.plugins.github import config
from src.plugins.github.dependencies import REPLY_TAG
from src.plugins.github.helpers import REPLY_ANY, NO_GITHUB_EVENT
from src.plugins.github.cache.message_tag import RepoTag, create_message_tag
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

repo = on_command(
    "repo",
    rule=NO_GITHUB_EVENT & REPLY_ANY,
    priority=config.github_command_priority,
    block=True,
)


@repo.handle()
async def handle_content(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    tag: REPLY_TAG,
):
    await create_message_tag(
        message_info, RepoTag(owner=tag.owner, repo=tag.repo, is_receive=True)
    )

    message = f"https://github.com/{tag.owner}/{tag.repo}"
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await repo.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await repo.send(message)

    tag = RepoTag(owner=tag.owner, repo=tag.repo, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
