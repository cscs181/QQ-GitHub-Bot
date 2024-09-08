"""
@Author         : yanyongyu
@Date           : 2023-11-27 13:32:08
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:44:44
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import logger, on_command
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.libs.github import FULLREPO_REGEX
from src.plugins.github.cache.message_tag import RepoTag, create_message_tag
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)
from src.plugins.github.dependencies import (
    REPOSITORY,
    OPTIONAL_REPLY_TAG,
    GITHUB_PUBLIC_CONTEXT,
    bypass_key,
)

license = on_command(
    "license",
    aliases={"许可证"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@license.handle()
async def parse_arg(
    state: T_State, tag: OPTIONAL_REPLY_TAG, arg: Message = CommandArg()
):
    # if arg is not empty, use arg as full_name
    if full_name := arg.extract_plain_text().strip():
        if not (matched := re.match(rf"^{FULLREPO_REGEX}$", full_name)):
            await license.finish(
                f"仓库名 {full_name} 错误！\n请重新发送正确的仓库名，"
                "例如：「/license owner/repo」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
    elif tag:
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["from_tag"] = True
    else:
        await license.finish(
            "请发送要查看 LICENSE 的仓库全名，例如：「/license owner/repo」"
        )


@license.handle(parameterless=(bypass_key("from_tag"),))
async def check_repo(repo: REPOSITORY): ...


@license.handle()
async def handle_content(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    context: GITHUB_PUBLIC_CONTEXT,
):
    owner: str = state["owner"]
    repo: str = state["repo"]

    await create_message_tag(
        message_info, RepoTag(owner=owner, repo=repo, is_receive=True)
    )

    try:
        async with context() as bot:
            resp = await bot.rest.repos.async_get(
                owner=owner,
                repo=repo,
            )
            repo_license = resp.parsed_data.license_
    except ActionTimeout:
        await license.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await license.finish("未找到该仓库的许可证")
        logger.opt(exception=e).error(f"Failed while getting repo license: {e}")
        await license.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting repo license: {e}")
        await license.finish("未知错误发生，请尝试重试或联系管理员")

    msg = (
        f"仓库 {owner}/{repo} 的许可证为 {repo_license.name}"
        if repo_license
        else f"仓库 {owner}/{repo} 没有设置许可证"
    )

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await license.send(msg)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await license.send(msg)

    tag = RepoTag(owner=owner, repo=repo, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
