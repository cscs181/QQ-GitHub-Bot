#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 15:15:02
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-15 17:42:10
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import re
import base64

from nonebot import on_regex
from nonebot.log import logger
from nonebot.rule import is_type
from nonebot.adapters import Event
from playwright.async_api import Error
from nonebot.plugin import PluginMetadata
from nonebot.params import Depends, RegexDict
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.models import Group
from src.plugins.github.utils import get_bot
from src.plugins.github.libs.renderer import issue_to_image
from src.plugins.github.libs.message_tag import IssueTag, create_message_tag
from src.plugins.github.helpers import (
    GROUP_EVENT,
    ISSUE_REGEX,
    FULLREPO_REGEX,
    GITHUB_ISSUE_OR_PR_LINK_REGEX,
    get_platform,
    get_message_info,
    get_current_group,
)

__plugin_meta__ = PluginMetadata(
    "GitHub Issue、PR 查看",
    "快速查看 GitHub Issue、PR 信息及事件",
    (
        "#number: 当群绑定了 GitHub 仓库时，快速查看 Issue、PR 信息及事件\n"
        "^owner/repo#number$: 快速查看 Issue、PR 信息及事件\n"
        "github.com/owner/repo/issues/number: 通过链接快速查看 Issue、PR 信息及事件"
    ),
)


issue = on_regex(
    rf"^{FULLREPO_REGEX}#{ISSUE_REGEX}$", priority=config.github_command_priority
)
link = on_regex(GITHUB_ISSUE_OR_PR_LINK_REGEX, priority=config.github_command_priority)


@issue.handle()
@link.handle()
async def handle(event: Event, group: dict[str, str] = RegexDict()):
    bot = get_bot()
    owner = group["owner"]
    repo = group["repo"]
    number = int(group["issue"])
    tag = IssueTag(owner=owner, repo=repo, issue_number=number)

    try:
        resp = await bot.rest.apps.async_get_repo_installation(owner=owner, repo=repo)
        context = bot.as_installation(resp.parsed_data.id)
    except ActionTimeout:
        await issue.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code != 404:
            logger.opt(exception=e).error(
                f"Failed while getting repo installation in issue: {e}"
            )
            await issue.finish("未知错误发生，请尝试重试或联系管理员")

        # not installed, try oauth app
        context = bot.as_oauth_app()

    try:
        with context:
            resp = await bot.rest.issues.async_get(
                owner=owner, repo=repo, issue_number=number
            )
            issue_ = resp.parsed_data
    except ActionTimeout:
        await issue.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code != 404:
            logger.opt(exception=e).error(
                f"Failed while getting repo installation in issue: {e}"
            )
            await issue.finish("未知错误发生，请尝试重试或联系管理员")
        await issue.finish(f"未找到 {owner}/{repo}#{number} 对应的 Issue 或 PR")

    if info := get_message_info(event):
        await create_message_tag(info, tag)

    try:
        with context:
            img = await issue_to_image(issue_)
    except ActionTimeout:
        await issue.finish("GitHub API 超时，请稍后再试")
    except Error:
        await issue.finish("生成图片出错！请稍后再试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating issue image: {e}")
        await issue_short.finish("生成图片出错！请稍后再试")

    if img:
        match get_platform(event):
            case "qq":
                result = await issue.send(QQMS.image(img))
                if isinstance(result, dict) and "message_id" in result:
                    await create_message_tag(
                        {"type": "qq", "message_id": result["message_id"]}, tag
                    )
            case _:
                logger.error(f"Unprocessed event type: {type(event)}")


issue_short = on_regex(
    rf"#{ISSUE_REGEX}",
    rule=is_type(*GROUP_EVENT),
    priority=config.github_command_priority,
)


@issue_short.handle()
async def handle_no_bind(group: None = Depends(get_current_group)):
    await issue_short.finish("此群未绑定 GitHub 仓库！")


@issue_short.handle()
async def handle_short(
    event: Event,
    group: Group = Depends(get_current_group),
    regex_group: dict[str, str] = RegexDict(),
):
    bot = get_bot()
    full_name = group.bind_repo
    number = int(regex_group["number"])
    owner, repo = full_name.split("/", maxsplit=1)
    tag = IssueTag(owner=owner, repo=repo, issue_number=number)

    try:
        resp = await bot.rest.apps.async_get_repo_installation(owner=owner, repo=repo)
        context = bot.as_installation(resp.parsed_data.id)
    except ActionTimeout:
        await issue_short.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code != 404:
            logger.opt(exception=e).error(
                f"Failed while getting repo installation in issue: {e}"
            )
            await issue_short.finish("未知错误发生，请尝试重试或联系管理员")

        # not installed, try oauth app
        context = bot.as_oauth_app()

    try:
        with context:
            resp = await bot.rest.issues.async_get(
                owner=owner, repo=repo, issue_number=number
            )
            issue_ = resp.parsed_data
    except ActionTimeout:
        await issue_short.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code != 404:
            logger.opt(exception=e).error(
                f"Failed while getting repo installation in issue: {e}"
            )
            await issue_short.finish("未知错误发生，请尝试重试或联系管理员")
        await issue_short.finish(f"未找到 {owner}/{repo}#{number} 对应的 Issue 或 PR")

    if info := get_message_info(event):
        await create_message_tag(info, tag)

    try:
        with context:
            img = await issue_to_image(issue_)
    except Error:
        await issue_short.finish("生成图片出错！请尝试重试")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while generating issue image: {e}")
        await issue_short.finish("生成图片出错！请稍后再试")

    if img:
        match get_platform(event):
            case "qq":
                result = await issue.send(QQMS.image(img))
                if isinstance(result, dict) and "message_id" in result:
                    await create_message_tag(
                        {"type": "qq", "message_id": result["message_id"]}, tag
                    )
            case _:
                logger.error(f"Unprocessed event type: {type(event)}")
