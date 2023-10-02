"""
@Author         : yanyongyu
@Date           : 2022-09-13 15:59:44
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-31 00:01:22
@Description    : Message tag lib
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Literal, Annotated, TypedDict

from pydantic import Field, BaseModel, parse_raw_as

from src.plugins.github.cache import get_message_tag as get_cache
from src.plugins.github.cache import create_message_tag as create_cache

from .platform import PLATFORMS


class MessageInfo(TypedDict):
    """Message info"""

    type: PLATFORMS
    message_id: str


class RepoTag(BaseModel):
    """Repo tag"""

    type: Literal["repo"] = "repo"
    owner: str
    repo: str
    is_receive: bool


class IssueTag(RepoTag):
    """Issue tag"""

    type: Literal["issue"] = "issue"
    number: int


class PullRequestTag(RepoTag):
    """Pull request tag"""

    type: Literal["pull_request"] = "pull_request"
    number: int


class CommitTag(RepoTag):
    """Commit tag"""

    type: Literal["commit"] = "commit"
    commit: str


Tag = Annotated[
    RepoTag | IssueTag | PullRequestTag | CommitTag, Field(discriminator="type")
]
"""Tag types"""


async def create_message_tag(info: MessageInfo, tag: Tag) -> None:
    """Create message tag"""
    await create_cache(info["type"], info["message_id"], tag.json())


async def get_message_tag(info: MessageInfo) -> Tag | None:
    """Get message tag"""
    cache = await get_cache(info["type"], info["message_id"])
    return parse_raw_as(Tag, cache) if cache else None
