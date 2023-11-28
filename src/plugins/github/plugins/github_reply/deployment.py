"""
@Author         : yanyongyu
@Date           : 2023-11-28 11:04:29
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-28 13:35:52
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from githubkit.utils import UNSET
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

deployment = on_command(
    "deployment",
    rule=NO_GITHUB_EVENT & REPLY_ANY,
    priority=config.github_command_priority,
    block=True,
)


@deployment.handle()
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
            resp = await bot.rest.repos.async_list_deployments(
                owner=tag.owner,
                repo=tag.repo,
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

    tag = RepoTag(owner=tag.owner, repo=tag.repo, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
