"""
@Author         : yanyongyu
@Date           : 2022-10-21 07:56:27
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 16:58:37
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from nonebot.typing import T_State
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot import logger, on_shell_command
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

label = on_shell_command(
    "label",
    aliases={"添加标签"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@label.handle()
async def parse_arg(
    state: T_State,
    user: AUTHORIZED_USER,  # command need auth
    tag: OPTIONAL_REPLY_TAG,
    arg: list[str | MessageSegment] = ShellCommandArgv(),
):
    args = [a for a in arg if isinstance(a, str)]
    # user reply to a issue or pr
    if isinstance(tag, IssueTag | PullRequestTag):
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["issue"] = tag.number
        state["labels"] = args
        state["is_pr"] = isinstance(tag, PullRequestTag)
        state["from_tag"] = True
    # user send both issue and labels
    elif len(args) >= 2:
        if not (matched := re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", args[0])):
            await label.finish(
                "Issue 或 PR 信息错误！\n请重新发送要添加标签的 Issue 或 PR，"
                "例如：「/label owner/repo#number bug」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["issue"] = matched["issue"]
        state["labels"] = args[1:]
    else:
        await label.finish(
            "请发送要添加标签的 Issue 或 PR，例如：「/label owner/repo#number bug」"
        )


@label.handle()
async def check_labels(state: T_State):
    if not state["labels"]:
        await label.reject(
            "添加的标签不能为空！请重新发送要添加标签的 Issue 或 PR\n"
            "例如：「/label owner/repo#number bug」"
        )


@label.handle(parameterless=(bypass_key("from_tag"),))
async def check_issue(state: T_State, issue: ISSUE):
    state["is_pr"] = bool(issue.pull_request)


@label.handle()
async def handle_label(
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
    labels: list[str] = state["labels"]

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
            await bot.rest.issues.async_add_labels(
                owner=owner,
                repo=repo,
                issue_number=number,
                labels=labels,
            )
    except ActionTimeout:
        await label.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await label.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        logger.opt(exception=e).error(f"Failed while label issue: {e}")
        await label.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while label issue: {e}")
        await label.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功为 {owner}/{repo}#{number} 添加了标签 {', '.join(labels)}"
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await label.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await label.send(message)

    tag = (
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
        if is_pr
        else IssueTag(owner=owner, repo=repo, number=number, is_receive=False)
    )
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
