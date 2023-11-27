"""
@Author         : yanyongyu
@Date           : 2021-04-26 18:19:15
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-27 14:12:45
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

import secrets

from nonebot import on_regex
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment as QQMS
from nonebot.adapters.qq import MessageSegment as QQOfficialMS

from src.plugins.github import config
from src.plugins.github.dependencies import (
    COMMIT,
    RELEASE,
    REPOSITORY,
    STORE_REGEX_VARS,
)
from src.providers.platform import (
    TARGET_INFO,
    MESSAGE_INFO,
    TargetType,
    extract_sent_message,
)
from src.plugins.github.cache.message_tag import (
    RepoTag,
    CommitTag,
    ReleaseTag,
    create_message_tag,
)
from src.plugins.github.helpers import (
    FULLREPO_REGEX,
    NO_GITHUB_EVENT,
    GITHUB_REPO_LINK_REGEX,
    GITHUB_COMMIT_LINK_REGEX,
    GITHUB_RELEASE_LINK_REGEX,
    GITHUB_PR_COMMIT_LINK_REGEX,
)

__plugin_meta__ = PluginMetadata(
    "GitHub OpenGraph 查看",
    "查看 GitHub 仓库，提交或发布的 OpenGraph",
    "^owner/repo$: 通过仓库缩写查看 OpenGraph\ngithub.com/owner/repo: 通过 GitHub"
    " 仓库链接查看 OpenGraph\ngithub.com/owner/repo/commit/<hash>: 通过 GitHub"
    " 提交链接查看 OpenGraph\ngithub.com/owner/repo/pull/<number>/commits/<hash>: 通过"
    " GitHub PR 提交链接查看 OpenGraph\ngithub.com/owner/repo/releases/tag/<tag>: 通过"
    " GitHub 发布链接查看 OpenGraph\n",
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


@repo_graph.handle(parameterless=(STORE_REGEX_VARS,))
@repo_link_graph.handle(parameterless=(STORE_REGEX_VARS,))
async def handle(
    target_info: TARGET_INFO, message_info: MESSAGE_INFO, repo: REPOSITORY
):
    await create_message_tag(
        message_info,
        RepoTag(owner=repo.owner.login, repo=repo.name, is_receive=True),
    )

    image_url = (
        f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
        f"{repo.owner.login}/{repo.name}"
    )
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await repo_graph.send(QQMS.image(image_url))
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await repo_graph.send(QQOfficialMS.image(image_url))

    tag = RepoTag(owner=repo.owner.login, repo=repo.name, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)


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


@commit_graph.handle(parameterless=(STORE_REGEX_VARS,))
@pr_commit_graph.handle(parameterless=(STORE_REGEX_VARS,))
async def handle_commit(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    commit: COMMIT,
):
    owner = state["owner"]
    repo = state["repo"]

    await create_message_tag(
        message_info,
        CommitTag(
            owner=owner,
            repo=repo,
            commit=commit.sha,
            is_receive=True,
        ),
    )

    image_url = (
        f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
        f"{owner}/{repo}/commit/{commit.sha}"
    )
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await commit_graph.send(QQMS.image(image_url))
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await commit_graph.send(QQOfficialMS.image(image_url))

    tag = CommitTag(owner=owner, repo=repo, commit=commit.sha, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)


release_graph = on_regex(
    GITHUB_RELEASE_LINK_REGEX,
    rule=NO_GITHUB_EVENT,
    priority=config.github_command_priority,
)


@release_graph.handle()
async def handle_release(
    state: T_State,
    target_info: TARGET_INFO,
    message_info: MESSAGE_INFO,
    release: RELEASE,
):
    owner = state["owner"]
    repo = state["repo"]

    await create_message_tag(
        message_info,
        ReleaseTag(
            owner=owner,
            repo=repo,
            tag=release.tag_name,
            is_receive=True,
        ),
    )

    image_url = (
        f"https://opengraph.githubassets.com/{secrets.token_urlsafe(16)}/"
        f"{owner}/{repo}/releases/tag/{release.tag_name}"
    )
    match target_info.type:
        case TargetType.QQ_USER | TargetType.QQ_GROUP:
            result = await release_graph.send(QQMS.image(image_url))
        case (
            TargetType.QQ_OFFICIAL_USER
            | TargetType.QQGUILD_USER
            | TargetType.QQ_OFFICIAL_GROUP
            | TargetType.QQGUILD_CHANNEL
        ):
            result = await release_graph.send(QQOfficialMS.image(image_url))

    tag = ReleaseTag(owner=owner, repo=repo, tag=release.tag_name, is_receive=False)
    if sent_message_info := extract_sent_message(target_info, result):
        await create_message_tag(sent_message_info, tag)
