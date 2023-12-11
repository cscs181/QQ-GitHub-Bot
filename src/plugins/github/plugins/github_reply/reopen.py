"""
@Author         : yanyongyu
@Date           : 2022-10-22 04:23:29
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 18:16:22
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
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT
from src.plugins.github.libs.github import ISSUE_REGEX, FULLREPO_REGEX
from src.plugins.github.cache.message_tag import (
    IssueTag,
    PullRequestTag,
    create_message_tag,
)
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

reopen = on_command(
    "reopen",
    aliases={"重新开启"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@reopen.handle()
async def parse_arg(
    state: T_State, tag: OPTIONAL_REPLY_TAG, arg: Message = CommandArg()
):
    # if arg is not empty, use arg as full_name
    if full_name := arg.extract_plain_text().strip():
        if not (matched := re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", full_name)):
            await reopen.finish(
                "Issue 或 PR 信息错误！\n请重新发送要重新开启的 Issue 或 PR，"
                "例如：「/reopen owner/repo#number」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["issue"] = matched["issue"]
    # user reply to a issue or pr
    elif isinstance(tag, IssueTag | PullRequestTag):
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["issue"] = tag.number
        state["is_pr"] = isinstance(tag, PullRequestTag)
        state["from_tag"] = True
    else:
        await reopen.finish(
            "请发送要重新开启的 Issue 或 PR，例如：「/reopen owner/repo#number」"
        )


@reopen.handle(parameterless=(bypass_key("from_tag"),))
async def check_issue(state: T_State, issue: ISSUE):
    state["is_pr"] = bool(issue.pull_request)


@reopen.handle()
async def handle_reopen(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    user: AUTHORIZED_USER,
):
    bot = get_github_bot()
    owner: str = state["owner"]
    repo: str = state["repo"]
    number: int = int(state["issue"])
    is_pr: bool = state["is_pr"]

    await create_message_tag(
        message_info,
        (
            PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True)
            if is_pr
            else IssueTag(owner=owner, repo=repo, number=number, is_receive=True)
        ),
    )

    try:
        async with bot.as_user(user.access_token):
            if not is_pr:
                await bot.rest.issues.async_update(
                    owner=owner,
                    repo=repo,
                    issue_number=number,
                    state="open",
                    state_reason="reopened",
                )
                message = f"已重新开启 Issue {owner}/{repo}#{number}"
            else:
                await bot.rest.pulls.async_update(
                    owner=owner, repo=repo, pull_number=number, state="open"
                )
                message = f"已重新开启 PR {owner}/{repo}#{number}"
    except ActionTimeout:
        await reopen.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await reopen.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        logger.opt(exception=e).error(f"Failed while reopen issue/pr: {e}")
        await reopen.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while reopen issue/pr: {e}")
        await reopen.finish("未知错误发生，请尝试重试或联系管理员")

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await reopen.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await reopen.send(message)

    tag = (
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
        if is_pr
        else IssueTag(owner=owner, repo=repo, number=number, is_receive=False)
    )
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
