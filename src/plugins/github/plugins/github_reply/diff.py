"""
@Author         : yanyongyu
@Date           : 2021-03-26 14:59:59
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:44:34
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import re

from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import logger, on_command
from nonebot.adapters.github import ActionTimeout
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS

from src.plugins.github import config
from src.plugins.github.libs.renderer import pr_diff_to_image
from src.plugins.github.libs.github import ISSUE_REGEX, FULLREPO_REGEX
from src.plugins.github.cache.message_tag import PullRequestTag, create_message_tag
from src.plugins.github.helpers import NO_GITHUB_EVENT, qqofficial_conditional_image
from src.plugins.github.dependencies import (
    ISSUE,
    OPTIONAL_REPLY_TAG,
    GITHUB_PUBLIC_CONTEXT,
)
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)

diff = on_command(
    "diff",
    aliases={"差异"},
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
    block=True,
)


@diff.handle()
async def parse_arg(
    state: T_State, tag: OPTIONAL_REPLY_TAG, arg: Message = CommandArg()
):
    # if arg is not empty, use arg as full_name
    if full_name := arg.extract_plain_text().strip():
        if not (matched := re.match(rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", full_name)):
            await diff.finish(
                "PR 信息错误！\n请重新发送要查看差异的 PR，"
                "例如：「/diff owner/repo#number」"
            )
        state["owner"] = matched["owner"]
        state["repo"] = matched["repo"]
        state["issue"] = matched["issue"]
    # user reply to a issue or pr
    elif isinstance(tag, PullRequestTag):
        state["owner"] = tag.owner
        state["repo"] = tag.repo
        state["issue"] = tag.number
        state["from_tag"] = True
    else:
        await diff.finish("请发送要查看差异的 PR，例如：「/diff owner/repo#number」")


@diff.handle()
async def check_issue(state: T_State, issue: ISSUE):
    if not issue.pull_request:
        await diff.finish(
            "该 issue 不是 PR！\n请重新发送要批准的 PR，"
            "例如：「/diff owner/repo#number」"
        )
    state["issue_info"] = issue


@diff.handle()
async def handle_diff(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    context: GITHUB_PUBLIC_CONTEXT,
):
    owner: str = state["owner"]
    repo: str = state["repo"]
    number: int = int(state["issue"])
    issue_info: ISSUE = state["issue_info"]

    await create_message_tag(
        message_info,
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True),
    )

    try:
        async with context() as bot:
            img = await pr_diff_to_image(bot, issue_info)
    except ActionTimeout:
        await diff.finish("GitHub API 超时，请稍后再试")
    except TimeoutError:
        await diff.finish("生成图片超时！请稍后再试")
    except Error:
        await diff.finish("生成图片出错！请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating issue image: {e}")
        await diff.finish("生成图片出错！请稍后再试")

    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await diff.send(QQMS.image(img))
        case TargetType.QQ_OFFICIAL_USER | TargetType.QQ_OFFICIAL_GROUP:
            result = await diff.send(await qqofficial_conditional_image(img))
        case TargetType.QQGUILD_USER | TargetType.QQGUILD_CHANNEL:
            result = await diff.send(QQOfficialMS.file_image(img))

    tag = PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
