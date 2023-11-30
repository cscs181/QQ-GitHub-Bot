"""
@Author         : yanyongyu
@Date           : 2023-11-27 13:32:08
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-29 16:46:34
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot import logger, on_command
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.helpers import REPLY_ANY, NO_GITHUB_EVENT
from src.plugins.github.cache.message_tag import RepoTag, create_message_tag
from src.plugins.github.dependencies import REPLY_TAG, GITHUB_PUBLIC_CONTEXT
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

license = on_command(
    "license",
    aliases={"许可证"},
    rule=NO_GITHUB_EVENT & REPLY_ANY,
    priority=config.github_command_priority,
    block=True,
)


@license.handle()
async def handle_content(
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    tag: REPLY_TAG,
    context: GITHUB_PUBLIC_CONTEXT,
):
    await create_message_tag(
        message_info, RepoTag(owner=tag.owner, repo=tag.repo, is_receive=True)
    )

    try:
        async with context as bot:
            resp = await bot.rest.repos.async_get(
                owner=tag.owner,
                repo=tag.repo,
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
        f"仓库 {tag.owner}/{tag.repo} 的许可证为 {repo_license.name}"
        if repo_license
        else f"仓库 {tag.owner}/{tag.repo} 没有设置许可证"
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

    tag = RepoTag(owner=tag.owner, repo=tag.repo, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
