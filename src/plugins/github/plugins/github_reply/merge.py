"""
@Author         : yanyongyu
@Date           : 2023-04-04 18:54:22
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-16 00:36:30
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re
from typing import Literal

from githubkit.utils import UNSET
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot import logger, on_command
from nonebot.exception import MatcherException
from nonebot.params import Command, CommandArg
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

MERGE_METHODS: dict[str, Literal["merge", "squash", "rebase"]] = {
    "merge": "merge",
    "squash": "squash",
    "rebase": "rebase",
    "合并": "merge",
    "压缩合并": "squash",
    "变基合并": "rebase",
}


merge = on_command(
    "merge",
    aliases={k for k in MERGE_METHODS if k != "merge"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@merge.handle()
async def parse_arg(
    state: T_State,
    user: AUTHORIZED_USER,  # command need auth
    tag: OPTIONAL_REPLY_TAG,
    action: tuple[str, ...] = Command(),
    arg: Message = CommandArg(),
):
    if (cmd := action[0]) not in MERGE_METHODS:
        await merge.finish(
            f"操作 {cmd} 不允许！\n请重新发送要合并的 PR，"
            "例如：「/merge owner/repo#number」"
        )

    state["cmd"] = cmd

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
            await merge.finish(
                "PR 信息错误！\n请重新发送要合并的 PR，"
                f"例如：「/{cmd} owner/repo#number」"
                f"或者「/{cmd} owner/repo#number title」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["issue"] = matched["issue"]
        state["content"] = args[1].strip() if len(args) == 2 else None
    else:
        await merge.finish(
            "请发送要合并的 PR，例如："
            f"「/{cmd} owner/repo#number」或者「/{cmd} owner/repo#number title」"
        )


@merge.handle(parameterless=(bypass_key("from_tag"),))
async def check_issue(state: T_State, issue: ISSUE):
    cmd = state["cmd"]
    if not issue.pull_request:
        await merge.finish(
            "该 issue 不是 PR！\n请重新发送要合并的 PR，"
            f"例如：「/{cmd} owner/repo#number」或者「/{cmd} owner/repo#number title」"
        )


@merge.handle()
async def handle_merge(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    user: AUTHORIZED_USER,
):
    bot = get_github_bot()
    cmd: str = state["cmd"]
    owner: str = state["owner"]
    repo: str = state["repo"]
    number: int = int(state["issue"])
    content: str | None = state["content"]

    await create_message_tag(
        message_info,
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True),
    )

    async with bot.as_user(user.access_token):
        try:
            pull_request = await bot.rest.pulls.async_get(
                owner=owner, repo=repo, pull_number=number
            )
            mergeable = pull_request.parsed_data.mergeable
        except ActionTimeout:
            await merge.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code == 404:
                await merge.finish(f"未找到 {owner}/{repo}#{number} 对应的 PR")
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")

        if mergeable is None:
            await merge.finish(
                f"GitHub 正在检查 PR {owner}/{repo}#{number} 是否可合并，请稍后再试"
            )
        elif mergeable is not True:
            await merge.finish(f"PR {owner}/{repo}#{number} 当前无法合并")

        try:
            await bot.rest.pulls.async_check_if_merged(
                owner=owner, repo=repo, pull_number=number
            )
            await merge.finish(f"PR {owner}/{repo}#{number} 已经合并")
        except MatcherException:
            raise
        except ActionTimeout:
            await merge.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code != 404:
                logger.opt(exception=e).error(f"Failed while merge pr: {e}")
                await merge.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")

        try:
            await bot.rest.pulls.async_merge(
                owner=owner,
                repo=repo,
                pull_number=number,
                merge_method=MERGE_METHODS[cmd],
                commit_title=content or UNSET,
            )
        except ActionTimeout:
            await merge.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code == 403:
                await merge.finish("权限不足，请尝试使用 /install 安装或刷新授权")
            elif e.response.status_code == 404:
                await merge.finish(f"未找到 {owner}/{repo}#{number} 对应的 PR")
            elif e.response.status_code == 405:
                await merge.finish(f"合并 {owner}/{repo}#{number} 请求不允许")
            # status code 409 not processed
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while merge pr: {e}")
            await merge.finish("未知错误发生，请尝试重试或联系管理员")

    message = f"成功合并了 PR {owner}/{repo}#{number}"
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await merge.send(message)
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await merge.send(message)

    tag = PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
