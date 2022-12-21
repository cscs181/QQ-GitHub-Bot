#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-04-26 18:19:15
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:51:32
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import secrets

from nonebot import on_regex
from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from nonebot.params import Depends, RegexDict
from githubkit.rest import Commit, Release, FullRepository
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.github import config
from src.plugins.github.libs.message_tag import RepoTag, CommitTag, create_message_tag
from src.plugins.github.helpers import (
    FULLREPO_REGEX,
    NO_GITHUB_EVENT,
    GITHUB_REPO_LINK_REGEX,
    GITHUB_COMMIT_LINK_REGEX,
    GITHUB_RELEASE_LINK_REGEX,
    GITHUB_PR_COMMIT_LINK_REGEX,
    get_platform,
    get_message_info,
)

from .dependencies import check_repo, check_commit, check_release

__plugin_meta__ = PluginMetadata(
    "GitHub OpenGraph 查看",
    "查看 GitHub 仓库，提交或发布的 OpenGraph",
    (
        "^owner/repo$: 通过仓库缩写查看 OpenGraph\n"
        "github.com/owner/repo: 通过 GitHub 仓库链接查看 OpenGraph\n"
        "github.com/owner/repo/commit/<hash>: 通过 GitHub 提交链接查看 OpenGraph\n"
        "github.com/owner/repo/pull/<number>/commits/<hash>: 通过 GitHub PR 提交链接查看 OpenGraph\n"
        "github.com/owner/repo/releases/tag/<tag>: 通过 GitHub 发布链接查看 OpenGraph\n"
    ),
)

repo_graph = on_regex(
    f"^{FULLREPO_REGEX}$", rule=NO_GITHUB_EVENT, priority=config.github_command_priority
)
# lower priority than issue link
repo_link_graph = on_regex(
    GITHUB_REPO_LINK_REGEX,
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority + 10,
)


@repo_graph.handle()
@repo_link_graph.handle()
async def handle(event: Event, repo: FullRepository = Depends(check_repo)):
    if info := get_message_info(event):
        await create_message_tag(
            info, RepoTag(owner=repo.owner.login, repo=repo.name, is_receive=True)
        )

    tag = RepoTag(owner=repo.owner.login, repo=repo.name, is_receive=False)
    match get_platform(event):
        case "qq":
            result = await repo_graph.send(
                QQMS.image(
                    f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                    f"{repo.owner.login}/{repo.name}"
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
    GITHUB_COMMIT_LINK_REGEX,
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)
pr_commit_graph = on_regex(
    GITHUB_PR_COMMIT_LINK_REGEX,
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@commit_graph.handle()
@pr_commit_graph.handle()
async def handle_commit(
    event: Event,
    commit: Commit = Depends(check_commit),
    group: dict[str, str] = RegexDict(),
):
    if info := get_message_info(event):
        await create_message_tag(
            info,
            CommitTag(
                owner=group["owner"],
                repo=group["repo"],
                commit=commit.sha,
                is_receive=True,
            ),
        )

    tag = CommitTag(
        owner=group["owner"], repo=group["repo"], commit=commit.sha, is_receive=False
    )
    match get_platform(event):
        case "qq":
            result = await commit_graph.send(
                QQMS.image(
                    f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                    f"{group['owner']}/{group['repo']}/commit/{commit.sha}"
                )
            )
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")


release_graph = on_regex(
    GITHUB_RELEASE_LINK_REGEX,
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@release_graph.handle()
async def handle_release(
    event: Event,
    release: Release = Depends(check_release),
    group: dict[str, str] = RegexDict(),
):
    if info := get_message_info(event):
        await create_message_tag(
            info,
            RepoTag(
                owner=group["owner"],
                repo=group["repo"],
                is_receive=True,
            ),
        )

    tag = RepoTag(owner=group["owner"], repo=group["repo"], is_receive=False)
    match get_platform(event):
        case "qq":
            result = await commit_graph.send(
                QQMS.image(
                    f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
                    f"{group['owner']}/{group['repo']}/releases/tag/{release.tag_name}"
                )
            )
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
