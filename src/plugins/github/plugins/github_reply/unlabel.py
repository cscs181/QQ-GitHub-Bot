"""
@Author         : yanyongyu
@Date           : 2022-10-21 08:13:17
@LastEditors    : yanyongyu
@LastEditTime   : 2023-12-11 17:08:22
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

unlabel = on_command(
    "unlabel",
    aliases={"移除标签"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@unlabel.handle()
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
        state["label"] = args[0] if args else None
        state["is_pr"] = isinstance(tag, PullRequestTag)
        state["from_tag"] = True
    # user send both issue and label
    elif len(args) == 2:
        if not (matched := re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", args[0])):
            await unlabel.finish(
                "Issue 或 PR 信息错误！\n请重新发送要移除标签的 Issue 或 PR，"
                "例如：「/unlabel owner/repo#number bug」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["issue"] = matched["issue"]
        state["label"] = args[1].strip()
    else:
        await unlabel.finish(
            "请发送要移除标签的 Issue 或 PR，例如：「/unlabel owner/repo#number bug」"
        )


@unlabel.handle()
async def check_label(state: T_State):
    if not (state["label"]):
        await unlabel.finish(
            "标签名不能为空！\n请重新发送要移除标签的 Issue 或 PR，"
            "例如：「/unlabel owner/repo#number bug」"
        )


@unlabel.handle(parameterless=(bypass_key("from_tag"),))
async def check_issue(state: T_State, issue: ISSUE):
    state["is_pr"] = bool(issue.pull_request)


@unlabel.handle()
async def handle_unlabel(
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
    label_: str = state["label"]

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
            await bot.rest.issues.async_remove_label(
                owner=owner, repo=repo, issue_number=number, name=label_
            )
    except ActionTimeout:
        await unlabel.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 403:
            await unlabel.finish("权限不足，请尝试使用 /install 安装或刷新授权")
        elif e.response.status_code == 404:
            await unlabel.finish(f"{owner}/{repo}#{number} 不存在标签 {label_}")
        logger.opt(exception=e).error(f"Failed while unlabel issue: {e}")
        await unlabel.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while unlabel issue: {e}")
        await unlabel.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功为 {owner}/{repo}#{number} 移除了标签 {label_}"
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await unlabel.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await unlabel.send(message)

    tag = (
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
        if is_pr
        else IssueTag(owner=owner, repo=repo, number=number, is_receive=False)
    )
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
