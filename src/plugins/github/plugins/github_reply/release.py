"""
@Author         : yanyongyu
@Date           : 2023-11-27 13:46:17
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:45:06
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re
import secrets

from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.libs.github import FULLREPO_REGEX
from src.plugins.github.cache.message_tag import ReleaseTag, create_message_tag
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

release = on_command(
    "release",
    aliases={"发布"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@release.handle()
async def parse_arg(
    state: T_State,
    tag: OPTIONAL_REPLY_TAG,
    arg: Message = CommandArg(),
):
    args = arg.extract_plain_text().strip().split(maxsplit=1)
    # user send both repo and tag or send repo only
    if len(args) == 2 or (args and ("/" in args[0] or tag is None)):
        if not (matched := re.match(rf"^{FULLREPO_REGEX}$", args[0])):
            await release.finish(
                f"仓库名 {args[0]} 错误！\n请重新发送正确的仓库名，"
                "例如：「/release owner/repo」或者「/release owner/repo tag」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["target_tag"] = args[1] if len(args) == 2 else None
    elif tag:
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["target_tag"] = (
            args[0] if args else (tag.tag if isinstance(tag, ReleaseTag) else None)
        )
        state["from_tag"] = True
    else:
        await release.finish(
            "请发送要查看发布的仓库全名，例如："
            "「/release owner/repo」或者「/release owner/repo tag」"
        )


@release.handle(parameterless=(bypass_key("from_tag"),))
async def check_repo(repo: REPOSITORY): ...


@release.handle()
async def handle_content(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    context: GITHUB_PUBLIC_CONTEXT,
):
    owner: str = state["owner"]
    repo: str = state["repo"]
    target_tag: str | None = state["target_tag"]

    try:
        async with context() as bot:
            if target_tag:
                resp = await bot.rest.repos.async_get_release_by_tag(
                    owner=owner, repo=repo, tag=target_tag
                )
            else:
                resp = await bot.rest.repos.async_get_latest_release(
                    owner=owner, repo=repo
                )
            release_data = resp.parsed_data
    except ActionTimeout:
        await release.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            if target_tag:
                await release.finish(f"找不到 {owner}/{repo} 的 {target_tag} 发布")
            else:
                await release.finish(f"找不到 {owner}/{repo} 的最新发布")
        logger.opt(exception=e).error(f"Failed while getting repo release: {e}")
        await release.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting repo release: {e}")
        await release.finish("未知错误发生，请尝试重试或联系管理员")

    await create_message_tag(
        message_info,
        ReleaseTag(
            owner=owner,
            repo=repo,
            tag=release_data.tag_name,
            is_receive=True,
        ),
    )

    image_url = (
        f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
        f"{owner}/{repo}/releases/tag/{release_data.tag_name}"
    )
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await release.send(QQMS.image(image_url))
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await release.send(QQOfficialMS.image(image_url))

    tag = ReleaseTag(
        owner=owner, repo=repo, tag=release_data.tag_name, is_receive=False
    )
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
