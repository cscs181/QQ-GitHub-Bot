"""
@Author         : yanyongyu
@Date           : 2023-03-04 17:55:56
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 16:45:48
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

comment = on_command(
    "comment",
    aliases={"reply", "评论", "回复"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@comment.handle()
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
        state["content"] = arg.extract_plain_text().strip()
        state["is_pr"] = isinstance(tag, PullRequestTag)
        state["from_tag"] = True
    # user send both issue and content
    elif len(args) == 2:
        if not (matched := re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", args[0])):
            await comment.finish(
                "Issue 或 PR 信息错误！\n请重新发送要评论的 Issue 或 PR，"
                "例如：「/comment owner/repo#number LGTM」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["issue"] = matched["issue"]
        state["content"] = args[1].strip()
    else:
        await comment.finish(
            "请发送要评论的 Issue 或 PR，例如：「/comment owner/repo#number LGTM」"
        )


@comment.handle()
async def check_content(state: T_State):
    if not state["content"]:
        await comment.finish(
            "评论内容不能为空！请重新发送要评论的内容\n"
            "例如：「/comment owner/repo#number LGTM」"
        )


@comment.handle(parameterless=(bypass_key("from_tag"),))
async def check_issue(state: T_State, issue: ISSUE):
    state["is_pr"] = bool(issue.pull_request)


@comment.handle()
async def handle_comment(
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
    content: str = state["content"]

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
            await bot.rest.issues.async_create_comment(
                owner=owner,
                repo=repo,
                issue_number=number,
                body=content,
            )
    except ActionTimeout:
        await comment.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await comment.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        logger.opt(exception=e).error(f"Failed while comment issue: {e}")
        await comment.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while comment issue: {e}")
        await comment.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功评论 {owner}/{repo}#{number}"
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await comment.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await comment.send(message)

    tag = (
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
        if is_pr
        else IssueTag(owner=owner, repo=repo, number=number, is_receive=False)
    )
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
