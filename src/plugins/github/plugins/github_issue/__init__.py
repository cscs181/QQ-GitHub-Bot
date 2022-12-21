#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 15:15:02
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:51:16
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Callable, AsyncContextManager

from nonebot import on_regex
from nonebot.log import logger
from githubkit.rest import Issue
from nonebot.rule import is_type
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.params import Depends, RegexDict
from playwright.async_api import Error, TimeoutError
from nonebot.adapters.github import GitHubBot, ActionTimeout
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.github import config
from src.plugins.github.models import User, Group
from src.plugins.github.libs.renderer import issue_to_image, pr_diff_to_image
from src.plugins.github.libs.message_tag import (
    IssueTag,
    PullRequestTag,
    create_message_tag,
)
from src.plugins.github.helpers import (
    GROUP_EVENT,
    ISSUE_REGEX,
    FULLREPO_REGEX,
    NO_GITHUB_EVENT,
    GITHUB_PR_FILE_LINK_REGEX,
    GITHUB_ISSUE_OR_PR_LINK_REGEX,
    get_platform,
    get_current_user,
    get_message_info,
    get_current_group,
)

from .dependencies import get_issue, get_context

__plugin_meta__ = PluginMetadata(
    "GitHub Issue、PR 查看",
    "快速查看 GitHub Issue、PR 相关信息及事件",
    (
        "#number: 当群绑定了 GitHub 仓库时，快速查看 Issue、PR 信息及事件\n"
        "^owner/repo#number$: 快速查看 Issue、PR 信息及事件\n"
        "github.com/owner/repo/(issues|pull)/number: 通过链接快速查看 Issue、PR 信息及事件\n"
        "github.com/owner/repo/pull/number/files: 通过链接快速查看 PR diff 信息"
    ),
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


@issue.handle()
@issue_link.handle()
async def handle_issue(
    event: Event,
    group: dict[str, str] = RegexDict(),
    issue_: Issue = Depends(get_issue),
    context: Callable[[], AsyncContextManager[GitHubBot]] = Depends(get_context),
):
    owner = group["owner"]
    repo = group["repo"]
    number = int(group["issue"])

    if info := get_message_info(event):
        await create_message_tag(
            info,
            PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True)
            if issue_.pull_request
            else IssueTag(owner=owner, repo=repo, number=number, is_receive=True),
        )

    try:
        async with context():
            img = await issue_to_image(issue_)
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
    match get_platform(event):
        case "qq":
            result = await issue.send(QQMS.image(img))
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")


pr_diff_link = on_regex(
    GITHUB_PR_FILE_LINK_REGEX,
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@pr_diff_link.handle()
async def handle_pr_diff(
    event: Event,
    group: dict[str, str] = RegexDict(),
    issue_: Issue = Depends(get_issue),
    context: Callable[[], AsyncContextManager[GitHubBot]] = Depends(get_context),
):
    owner = group["owner"]
    repo = group["repo"]
    number = int(group["issue"])

    if info := get_message_info(event):
        await create_message_tag(
            info, PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True)
        )

    try:
        async with context():
            img = await pr_diff_to_image(issue_)
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
    match get_platform(event):
        case "qq":
            result = await pr_diff_link.send(QQMS.image(img))
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")


issue_short = on_regex(
    rf"^#{ISSUE_REGEX}$",
    rule=is_type(*GROUP_EVENT) & NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@issue_short.handle()
async def handle_no_bind(group: None = Depends(get_current_group)):
    await issue_short.finish("此群未绑定 GitHub 仓库！")


@issue_short.handle()
async def handle_short(
    event: Event,
    matcher: Matcher,
    user: User | None = Depends(get_current_user),
    group: Group = Depends(get_current_group),
    regex_group: dict[str, str] = RegexDict(),
):
    number = int(regex_group["issue"])
    owner, repo = group.bind_repo.split("/", maxsplit=1)
    info = {"owner": owner, "repo": repo, "issue": number}

    context = await get_context(matcher, info, user)
    issue_ = await get_issue(matcher, info, context)

    if info := get_message_info(event):
        await create_message_tag(
            info,
            PullRequestTag(owner=owner, repo=repo, number=number, is_receive=True)
            if issue_.pull_request
            else IssueTag(owner=owner, repo=repo, number=number, is_receive=True),
        )

    try:
        async with context():
            img = await issue_to_image(issue_)
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
    match get_platform(event):
        case "qq":
            result = await issue_short.send(QQMS.image(img))
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
