#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-04-26 18:19:15
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 04:54:14
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import secrets

from nonebot import on_regex
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS

from src.plugins.github import config
from src.plugins.github.helpers import (
    FULLREPO_REGEX,
    GITHUB_REPO_LINK_REGEX,
    GITHUB_COMMIT_LINK_REGEX,
    GITHUB_PR_COMMIT_LINK_REGEX,
)

from .dependencies import check_repo, check_commit

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
async def handle(repo: str = Depends(check_repo)):
    await repo_graph.finish(
        QQMS.image(
            f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/{repo}"
        )
    )


commit_graph = on_regex(
    GITHUB_COMMIT_LINK_REGEX, priority=config.github_command_priority
)
pr_commit_graph = on_regex(
    GITHUB_PR_COMMIT_LINK_REGEX, priority=config.github_command_priority
)


@commit_graph.handle()
@pr_commit_graph.handle()
async def handle_commit(commit: str = Depends(check_commit)):
    await commit_graph.finish(
        QQMS.image(
            f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/{commit}"
        )
    )
