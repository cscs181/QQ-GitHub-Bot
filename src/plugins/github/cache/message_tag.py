"""
@Author         : yanyongyu
@Date           : 2022-09-13 15:56:01
@LastEditors    : yanyongyu
@LastEditTime   : 2024-03-05 14:48:21
@Description    : Message tag cache
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from datetime import timedelta
from typing import Literal, Annotated

from pydantic import Field, BaseModel, TypeAdapter

from src.providers.redis import redis_client
from src.providers.platform import MessageInfo

MESSAGE_TAG_CACHE_KEY = "cache:github:message:{type}:{message_id}:tag"
MESSAGE_TAG_CACHE_EXPIRE = timedelta(days=1)


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


class ReleaseTag(RepoTag):
    """Release tag"""

    type: Literal["release"] = "release"
    tag: str


Tag = Annotated[
    RepoTag | IssueTag | PullRequestTag | CommitTag | ReleaseTag,
    Field(discriminator="type"),
]
"""Tag types"""


async def create_message_tag(message: MessageInfo, tag: Tag) -> None:
    """Create message tag cache

    Args:
        message: Message info
        tag: Tag data
    """

    await redis_client.set(
        MESSAGE_TAG_CACHE_KEY.format(
            type=message.type.value, message_id=str(message.id)
        ),
        tag.model_dump_json(),
        ex=MESSAGE_TAG_CACHE_EXPIRE,
    )


async def get_message_tag(message: MessageInfo) -> Tag | None:
    """Get message tag cache

    Args:
        platform: Platform name
        message_id: Message id

    Returns:
        Existing tag data
    """
    data: bytes | None
    if (
        data := await redis_client.get(
            MESSAGE_TAG_CACHE_KEY.format(
                type=message.type.value, message_id=str(message.id)
            )
        )
    ) is not None:
        return TypeAdapter(Tag).validate_json(data)
