"""
@Author         : yanyongyu
@Date           : 2022-10-22 03:59:07
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 16:49:25
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

ISSUE_CLOSE_REASON = ("completed", "not_planned")

close = on_command(
    "close",
    aliases={"关闭"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@close.handle()
async def parse_arg(
    state: T_State,
    user: AUTHORIZED_USER,  # command need auth
    tag: OPTIONAL_REPLY_TAG,
    arg: Message = CommandArg(),
):
    args = arg.extract_plain_text().strip().split(maxsplit=1)
    # user reply to a issue or pr
    if isinstance(tag, IssueTag | PullRequestTag):
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["issue"] = tag.number
        state["reason"] = args[0] if args else None
        state["is_pr"] = isinstance(tag, PullRequestTag)
        state["from_tag"] = True
    # user send both issue and reason
    elif args:
        if not (matched := re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", args[0])):
            await close.finish(
                "Issue 或 PR 信息错误！\n请重新发送要关闭的 Issue 或 PR，"
                "例如：「/close owner/repo#number」或者"
                "「/close owner/repo#number not_planned」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["issue"] = matched["issue"]
        state["reason"] = args[1].strip() if len(args) == 2 else None
    else:
        await close.finish(
            "请发送要关闭的 Issue 或 PR，例如："
            "「/close owner/repo#number」或者「/close owner/repo#number not_planned」"
        )


@close.handle()
async def check_reason(state: T_State):
    if (reason := state["reason"]) and reason not in ISSUE_CLOSE_REASON:
        await close.finish(
            f"关闭原因 {reason} 错误！"
            f"关闭原因必须是 {'/'.join(ISSUE_CLOSE_REASON)}，请重新发送\n"
            "例如：「/close owner/repo#number」或者"
            "「/close owner/repo#number not_planned」"
        )


@close.handle(parameterless=(bypass_key("from_tag"),))
async def check_issue(state: T_State, issue: ISSUE):
    state["is_pr"] = bool(issue.pull_request)


@close.handle()
async def handle_close(
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
    reason: str | None = state["reason"]

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
                    state="closed",
                    state_reason=reason or UNSET,  # type: ignore
                )
                message = f"已关闭 Issue {owner}/{repo}#{number}"
            else:
                await bot.rest.pulls.async_update(
                    owner=owner,
                    repo=repo,
                    pull_number=number,
                    state="closed",
                )
                message = f"已关闭 PR {owner}/{repo}#{number}"
    except ActionTimeout:
        await close.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await close.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        logger.opt(exception=e).error(f"Failed while close pr: {e}")
        await close.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while close pr: {e}")
        await close.finish("未知错误发生，请尝试重试或联系管理员")

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await close.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await close.send(message)

    tag = (
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
        if is_pr
        else IssueTag(owner=owner, repo=repo, number=number, is_receive=False)
    )
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
