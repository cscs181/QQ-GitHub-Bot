"""
@Author         : yanyongyu
@Date           : 2023-11-27 13:46:17
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-27 14:13:09
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import secrets

from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.helpers import REPLY_ANY, NO_GITHUB_EVENT
from src.plugins.github.dependencies import REPLY_TAG, GITHUB_PUBLIC_CONTEXT
from src.plugins.github.cache.message_tag import ReleaseTag, create_message_tag
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

release = on_command(
    "release",
    rule=NO_GITHUB_EVENT & REPLY_ANY,
    priority=config.github_command_priority,
    block=True,
)


@release.handle()
async def handle_content(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    tag: REPLY_TAG,
    context: GITHUB_PUBLIC_CONTEXT,
    args: Message = CommandArg(),
):
    cmd_arg = args.extract_plain_text().strip()
    target_tag = cmd_arg and (tag.tag if isinstance(tag, ReleaseTag) else None)
    try:
        async with context as bot:
            if target_tag:
                resp = await bot.rest.repos.async_get_release_by_tag(
                    owner=tag.owner, repo=tag.repo, tag=target_tag
                )
            else:
                resp = await bot.rest.repos.async_get_latest_release(
                    owner=tag.owner, repo=tag.repo
                )
            release_data = resp.parsed_data
    except ActionTimeout:
        await release.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            if target_tag:
                await release.finish(
                    f"找不到 {tag.owner}/{tag.repo} 的 {target_tag} 发布"
                )
            else:
                await release.finish(f"找不到 {tag.owner}/{tag.repo} 的最新发布")
        logger.opt(exception=e).error(f"Failed while getting repo release: {e}")
        await release.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while getting repo release: {e}")
        await release.finish("未知错误发生，请尝试重试或联系管理员")

    await create_message_tag(
        message_info,
        ReleaseTag(
            owner=tag.owner,
            repo=tag.repo,
            tag=release_data.tag_name,
            is_receive=True,
        ),
    )

    image_url = (
        f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
        f"{tag.owner}/{tag.repo}/releases/tag/{release_data.tag_name}"
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
        owner=tag.owner, repo=tag.repo, tag=release_data.tag_name, is_receive=False
    )
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
