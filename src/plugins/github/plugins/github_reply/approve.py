"""
@Author         : yanyongyu
@Date           : 2022-10-21 07:08:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 18:06:16
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
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.libs.github import ISSUE_REGEX, FULLREPO_REGEX
from src.plugins.github.cache.message_tag import PullRequestTag, create_message_tag
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)
from src.plugins.github.dependencies import (
    ISSUE,
    AUTHORIZED_USER,
    OPTIONAL_REPLY_TAG,
    bypass_key,
)

approve = on_command(
    "approve",
    aliases={"批准"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@approve.handle()
async def parse_arg(
    state: T_State,
    user: AUTHORIZED_USER,  # command need auth
    tag: OPTIONAL_REPLY_TAG,
    arg: Message = CommandArg(),
):
    args = arg.extract_plain_text().strip().split(maxsplit=1)
    # user reply to a issue or pr
    if isinstance(tag, PullRequestTag):
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["issue"] = tag.number
        state["content"] = arg.extract_plain_text().strip()
        state["from_tag"] = True
    # user send both issue and content
    elif args:
        if not (matched := re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", args[0])):
            await approve.finish(
                "PR 信息错误！\n请重新发送要批准的 PR，"
                "例如：「/approve owner/repo#number」或者"
                "「/approve owner/repo#number LGTM」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["issue"] = matched["issue"]
        state["content"] = args[1].strip() if len(args) == 2 else None
    else:
        await approve.finish(
            "请发送要批准的 PR，例如："
            "「/approve owner/repo#number」或者「/approve owner/repo#number LGTM」"
        )


@approve.handle(parameterless=(bypass_key("from_tag"),))
async def check_issue(state: T_State, issue: ISSUE):
    if not issue.pull_request:
        await approve.finish(
            "该 issue 不是 PR！\n请重新发送要批准的 PR，"
            "例如：「/approve owner/repo#number」或者"
            "「/approve owner/repo#number LGTM」"
        )


@approve.handle()
async def handle_approve(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    user: AUTHORIZED_USER,
):
    bot = get_github_bot()
    owner: str = state["owner"]
    repo: str = state["repo"]
    number: int = int(state["issue"])
    content: str = state["content"]

    await create_message_tag(
        message_info,
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True),
    )

    try:
        async with bot.as_user(user.access_token):
            await bot.rest.pulls.async_create_review(
                owner=owner,
                repo=repo,
                pull_number=number,
                event="APPROVE",
                body=content or UNSET,
            )
    except ActionTimeout:
        await approve.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await approve.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        elif e.response.status_code == 404:
            await approve.finish("批准 PR 失败，可能是因为 PR 已经被合并或关闭")
        elif e.response.status_code == 422:
            await approve.finish("批准 PR 失败，可能是因为不能批准自己的 PR")
        logger.opt(exception=e).error(f"Failed while approve pr: {e}")
        await approve.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while approve pr: {e}")
        await approve.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功批准了 PR {owner}/{repo}#{number}"
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await approve.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await approve.send(message)

    tag = PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
