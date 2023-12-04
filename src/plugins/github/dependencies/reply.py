"""
@Author         : yanyongyu
@Date           : 2023-10-08 14:02:23
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-30 12:13:04
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.matcher import Matcher

from src.plugins.github.models import Group
from src.providers.platform import OPTIONAL_GROUP_INFO, OPTIONAL_REPLY_MESSAGE_INFO
from src.plugins.github.cache.message_tag import (
    Tag,
    RepoTag,
    IssueTag,
    PullRequestTag,
    get_message_tag,
)


async def get_reply_tag(
    reply_info: OPTIONAL_REPLY_MESSAGE_INFO,
    group_info: OPTIONAL_GROUP_INFO,
) -> Tag | None:
    # get tag from cache if reply anything
    if reply_info:
        return await get_message_tag(reply_info)
    # else create tag from group binded repo
    if group_info and (group := await Group.from_info(group_info)) and group.bind_repo:
        owner, repo = group.bind_repo.split("/")
        return RepoTag(owner=owner, repo=repo, is_receive=True)


OPTIONAL_REPLY_TAG: TypeAlias = Annotated[
    Tag | None, Depends(get_reply_tag, use_cache=True)
]
"""Replied message tag."""


async def ensure_reply_tag(matcher: Matcher, reply_tag: OPTIONAL_REPLY_TAG) -> Tag:
    if reply_tag is None:
        logger.error("Reply tag not found")
        await matcher.finish()
    return reply_tag


REPLY_TAG: TypeAlias = Annotated[Tag, Depends(ensure_reply_tag)]


async def get_issue_or_pr_reply_tag(
    matcher: Matcher, tag: OPTIONAL_REPLY_TAG
) -> IssueTag | PullRequestTag:
    """Get issue or pull request reply tag from replied message info.

    Finish the session if the tag do not exists or is not issue or pull request tag.
    """
    if not tag or not isinstance(tag, IssueTag | PullRequestTag):
        await matcher.finish()
    return tag


ISSUE_OR_PR_REPLY_TAG: TypeAlias = Annotated[
    IssueTag | PullRequestTag, Depends(get_issue_or_pr_reply_tag)
]
"""Issue or pull request replied message tag.

Finish the session if the tag do not exists or is not issue or pull request tag.
"""


async def get_pr_reply_tag(matcher: Matcher, tag: OPTIONAL_REPLY_TAG) -> PullRequestTag:
    """Get pull request reply tag from replied message info.

    Finish the session if the tag do not exists or is not pull request tag.
    """
    if not tag or not isinstance(tag, PullRequestTag):
        await matcher.finish()
    return tag


PR_REPLY_TAG: TypeAlias = Annotated[PullRequestTag, Depends(get_pr_reply_tag)]
"""Pull request replied message tag.

Finish the session if the tag do not exists or is not pull request tag.
"""


async def store_tag_data(state: T_State, tag: OPTIONAL_REPLY_TAG) -> None:
    if tag:
        state["owner"] = tag.owner
        state["repo"] = tag.repo

        if isinstance(tag, IssueTag | PullRequestTag):
            state["issue"] = tag.number


STORE_TAG_DATA = Depends(store_tag_data)
"""Parameterless dependency that stores tag data to state."""
