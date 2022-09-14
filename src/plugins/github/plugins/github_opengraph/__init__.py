#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-04-26 18:19:15
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 11:05:30
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import secrets

from nonebot import on_regex
from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.github import config
from src.plugins.github.libs.message_tag import RepoTag, CommitTag, create_message_tag
from src.plugins.github.helpers import (
    FULLREPO_REGEX,
    GITHUB_REPO_LINK_REGEX,
    GITHUB_COMMIT_LINK_REGEX,
    GITHUB_PR_COMMIT_LINK_REGEX,
    get_platform,
    get_message_info,
)

from .dependencies import RepoID, CommitID, check_repo, check_commit

__plugin_meta__ = PluginMetadata(
    "GitHub OpenGraph 查看",
    "查看 GitHub 仓库或提交的 OpenGraph",
    (
        "^owner/repo$: 通过仓库缩写查看 OpenGraph\n"
        "github.com/owner/repo: 通过 GitHub 仓库链接查看 OpenGraph\n"
        "github.com/owner/repo/commit/commit-hash: 通过 GitHub 提交链接查看 OpenGraph\n"
        "github.com/owner/repo/pull/pull-number/commits/commit-hash: 通过 GitHub PR 提交链接查看 OpenGraph"
    ),
)

repo_graph = on_regex(f"^{FULLREPO_REGEX}$", priority=config.github_command_priority)
# lower priority than issue link
repo_link_graph = on_regex(
    GITHUB_REPO_LINK_REGEX, priority=config.github_command_priority + 1
)


@repo_graph.handle()
@repo_link_graph.handle()
async def handle(event: Event, repo: RepoID = Depends(check_repo)):
    if not (info := get_message_info(event)):
        await repo_graph.finish()

    tag = RepoTag(owner=repo["owner"], repo=repo["repo"])
    await create_message_tag(info, tag)

    match get_platform(event):
        case "qq":
            result = await repo_graph.send(
                QQMS.image(
                    f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                    f"{repo['owner']}/{repo['repo']}"
                )
            )
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]},
                    tag,
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")


commit_graph = on_regex(
    GITHUB_COMMIT_LINK_REGEX, priority=config.github_command_priority
)
pr_commit_graph = on_regex(
    GITHUB_PR_COMMIT_LINK_REGEX, priority=config.github_command_priority
)


@commit_graph.handle()
@pr_commit_graph.handle()
async def handle_commit(event: Event, commit: CommitID = Depends(check_commit)):
    if not (info := get_message_info(event)):
        await commit_graph.finish()

    tag = CommitTag(owner=commit["owner"], repo=commit["repo"], commit=commit["commit"])
    await create_message_tag(info, tag)

    match get_platform(event):
        case "qq":
            result = await commit_graph.send(
                QQMS.image(
                    f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                    f"{commit['owner']}/{commit['repo']}/commit/{commit['commit']}"
                )
            )
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
