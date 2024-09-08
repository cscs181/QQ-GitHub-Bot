"""
@Author         : yanyongyu
@Date           : 2023-11-28 11:04:29
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:44:27
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from githubkit.utils import UNSET
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

deployment = on_command(
    "deployment",
    aliases={"部署", "部署记录"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@deployment.handle()
async def parse_arg(
    state: T_State, tag: OPTIONAL_REPLY_TAG, arg: Message = CommandArg()
):
    # if arg is not empty, use arg as full_name
    if full_name := arg.extract_plain_text().strip():
        if not (matched := re.match(rf"^{FULLREPO_REGEX}$", full_name)):
            await deployment.finish(
                f"仓库名 {full_name} 错误！\n请重新发送正确的仓库名，"
                "例如：「/deployment owner/repo」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
    elif tag:
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["from_tag"] = True
    else:
        await deployment.finish(
            "请发送要查看部署的仓库全名，例如：「/deployment owner/repo」"
        )


@deployment.handle(parameterless=(bypass_key("from_tag"),))
async def check_repo(repo: REPOSITORY): ...


@deployment.handle()
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
            resp = await bot.rest.repos.async_list_deployments(
                owner=owner,
                repo=repo,
                sha=UNSET,
                ref=UNSET,
                task=UNSET,
                environment=UNSET,
                per_page=3,
            )
            result = resp.parsed_data
    except ActionTimeout:
        await deployment.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        logger.opt(exception=e).error(f"Failed while getting repo readme: {e}")
        await deployment.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting repo readme: {e}")
        await deployment.finish("未知错误发生，请尝试重试或联系管理员")

    if not result:
        msg = "该仓库没有部署记录"
    else:
        msg = "\n\n".join(
            f"Deploy ID: {d.id}"
            + f"\nDeployed to {d.environment}"
            + (f" by {d.creator.login}" if d.creator else "")
            + f"\n创建于 {d.created_at.isoformat()}"
            + (
                f"\n更新于 {d.updated_at.isoformat()}"
                if d.updated_at != d.created_at
                else ""
            )
            for d in result
        )

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await deployment.send(msg)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await deployment.send(msg)

    tag = RepoTag(owner=owner, repo=repo, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
