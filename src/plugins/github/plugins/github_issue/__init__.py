"""
@Author         : yanyongyu
@Date           : 2021-03-09 15:15:02
@LastEditors    : yanyongyu
@LastEditTime   : 2024-09-08 11:44:07
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"


from nonebot.typing import T_State
from nonebot import logger, on_regex
from nonebot.plugin import PluginMetadata
from nonebot.adapters.github import ActionTimeout
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS

from src.plugins.github import config
from src.plugins.github.libs.renderer import issue_to_image, pr_diff_to_image
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
from src.plugins.github.helpers import (
    NO_GITHUB_EVENT,
    MATCH_WHEN_GROUP,
    qqofficial_conditional_image,
)
from src.plugins.github.dependencies import (
    ISSUE,
    BINDED_GROUP,
    STORE_REGEX_VARS,
    GITHUB_PUBLIC_CONTEXT,
)
from src.plugins.github.libs.github import (
    ISSUE_REGEX,
    FULLREPO_REGEX,
    GITHUB_PR_FILE_LINK_REGEX,
    GITHUB_ISSUE_OR_PR_LINK_REGEX,
)

__plugin_meta__ = PluginMetadata(
    "GitHub Issue、PR 查看",
    "快速查看 GitHub Issue、PR 相关信息及事件",
    "#number: 当群绑定了 GitHub 仓库时，快速查看 Issue、PR 信息及事件\n"
    "^owner/repo#number$: 快速查看 Issue、PR 信息及事件\n"
    "github.com/owner/repo/(issues|pull)/number: "
    "通过链接快速查看 Issue、PR 信息及事件\n"
    "github.com/owner/repo/pull/number/files: 通过链接快速查看 PR diff 信息",
)


issue = on_regex(
    rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$",
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)
issue_link = on_regex(
    GITHUB_ISSUE_OR_PR_LINK_REGEX,
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority + 1,
)


@issue.handle(parameterless=(STORE_REGEX_VARS,))
@issue_link.handle(parameterless=(STORE_REGEX_VARS,))
async def handle_issue(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    issue_: ISSUE,
    context: GITHUB_PUBLIC_CONTEXT,
):
    owner = state["owner"]
    repo = state["repo"]
    number = int(state["issue"])
    comment = int(comment) if (comment := state.get("comment")) else None

    await create_message_tag(
        message_info,
        (
            PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True)
            if issue_.pull_request
            else IssueTag(owner=owner, repo=repo, number=number, is_receive=True)
        ),
    )

    try:
        async with context() as bot:
            img = await issue_to_image(bot, issue_, highlight_comment=comment)
    except ActionTimeout:
        await issue.finish("GitHub API 超时，请稍后再试")
    except TimeoutError:
        await issue.finish("生成图片超时！请稍后再试")
    except Error:
        await issue.finish("生成图片出错！请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating issue image: {e}")
        await issue.finish("生成图片出错！请稍后再试")

    tag = (
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
        if issue_.pull_request
        else IssueTag(owner=owner, repo=repo, number=number, is_receive=False)
    )
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await issue.send(QQMS.image(img))
        case TargetType.QQ_OFFICIAL_USER | TargetType.QQ_OFFICIAL_GROUP:
            result = await issue.send(await qqofficial_conditional_image(img))
        case TargetType.QQGUILD_USER | TargetType.QQGUILD_CHANNEL:
            result = await issue.send(QQOfficialMS.file_image(img))

    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)


pr_diff_link = on_regex(
    GITHUB_PR_FILE_LINK_REGEX,
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@pr_diff_link.handle(parameterless=(STORE_REGEX_VARS,))
async def handle_pr_diff(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    issue_: ISSUE,
    context: GITHUB_PUBLIC_CONTEXT,
):
    owner = state["owner"]
    repo = state["repo"]
    number = int(state["issue"])

    await create_message_tag(
        message_info,
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True),
    )

    try:
        async with context() as bot:
            img = await pr_diff_to_image(bot, issue_)
    except ActionTimeout:
        await pr_diff_link.finish("GitHub API 超时，请稍后再试")
    except TimeoutError:
        await pr_diff_link.finish("生成图片超时！请稍后再试")
    except Error:
        await pr_diff_link.finish("生成图片出错！请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating pr diff image: {e}")
        await pr_diff_link.finish("生成图片出错！请稍后再试")

    tag = PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await pr_diff_link.send(QQMS.image(img))
        case TargetType.QQ_OFFICIAL_USER | TargetType.QQ_OFFICIAL_GROUP:
            result = await pr_diff_link.send(await qqofficial_conditional_image(img))
        case TargetType.QQGUILD_USER | TargetType.QQGUILD_CHANNEL:
            result = await pr_diff_link.send(QQOfficialMS.file_image(img))

    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)


issue_short = on_regex(
    rf"^#{ISSUE_REGEX}$",
    rule=MATCH_WHEN_GROUP & NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@issue_short.handle(parameterless=(STORE_REGEX_VARS,))
async def check_bind(state: T_State, group: BINDED_GROUP):
    state["owner"], state["repo"] = group.bind_repo.split("/", maxsplit=1)


@issue_short.handle()
async def handle_short(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    issue_: ISSUE,
    context: GITHUB_PUBLIC_CONTEXT,
):
    owner = state["owner"]
    repo = state["repo"]
    number = int(state["issue"])

    await create_message_tag(
        message_info,
        (
            PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True)
            if issue_.pull_request
            else IssueTag(owner=owner, repo=repo, number=number, is_receive=True)
        ),
    )

    try:
        async with context() as bot:
            img = await issue_to_image(bot, issue_)
    except TimeoutError:
        await issue_short.finish("生成图片超时！请尝试重试")
    except Error:
        await issue_short.finish("生成图片出错！请尝试重试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating issue image: {e}")
        await issue_short.finish("生成图片出错！请稍后再试")

    tag = (
        PullRequestTag(owner=owner, repo=repo, number=number, is_receive=False)
        if issue_.pull_request
        else IssueTag(owner=owner, repo=repo, number=number, is_receive=False)
    )
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await issue_short.send(QQMS.image(img))
        case TargetType.QQ_OFFICIAL_USER | TargetType.QQ_OFFICIAL_GROUP:
            result = await issue_short.send(await qqofficial_conditional_image(img))
        case TargetType.QQGUILD_USER | TargetType.QQGUILD_CHANNEL:
            result = await issue_short.send(QQOfficialMS.file_image(img))

    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
