"""
@Author         : yanyongyu
@Date           : 2022-10-21 01:30:44
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 15:59:03
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg

from src.plugins.github import config
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.libs.github import FULLREPO_REGEX
from src.plugins.github.cache.message_tag import RepoTag, create_message_tag
from src.plugins.github.dependencies import REPOSITORY, OPTIONAL_REPLY_TAG, bypass_key
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

repo = on_command(
    "repo",
    aliases={"仓库"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@repo.handle()
async def parse_arg(
    state: T_State, tag: OPTIONAL_REPLY_TAG, arg: Message = CommandArg()
):
    # if arg is not empty, use arg as full_name
    if full_name := arg.extract_plain_text().strip():
        if not (matched := re.match(rf"^{FULLREPO_REGEX}$", full_name)):
            await repo.finish(
                f"仓库名 {full_name} 错误！\n请重新发送正确的仓库名，"
                "例如：「/repo owner/repo」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
    elif tag:
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["from_tag"] = True
    else:
        await repo.finish("请发送要查看的仓库全名，例如：「/repo owner/repo」")


@repo.handle(parameterless=(bypass_key("from_tag"),))
async def check_repo(repo: REPOSITORY): ...


@repo.handle()
async def handle_content(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
):
    owner: str = state["owner"]
    repo_name: str = state["repo"]

    await create_message_tag(
        message_info, RepoTag(owner=owner, repo=repo_name, is_receive=True)
    )

    message = f"https://github.com/{owner}/{repo_name}"
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

    tag = RepoTag(owner=owner, repo=repo_name, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
