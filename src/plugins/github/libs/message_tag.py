#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-13 15:59:44
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-06 06:01:54
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Literal, Annotated, TypedDict

from pydantic import Field, BaseModel, parse_raw_as

from src.plugins.github.cache import get_message_tag as get_cache
from src.plugins.github.cache import create_message_tag as create_cache

from .platform import PLATFORMS


class MessageInfo(TypedDict):
    type: PLATFORMS
    message_id: str


class RepoTag(BaseModel):
    type: Literal["repo"] = "repo"
    owner: str
    repo: str
    is_receive: bool


class IssueTag(RepoTag):
    type: Literal["issue"] = "issue"
    number: int


class PullRequestTag(RepoTag):
    type: Literal["pull_request"] = "pull_request"
    number: int


class CommitTag(RepoTag):
    type: Literal["commit"] = "commit"
    commit: str


Tag = Annotated[
    RepoTag | IssueTag | PullRequestTag | CommitTag, Field(discriminator="type")
]


async def create_message_tag(info: MessageInfo, tag: Tag):
    await create_cache(info["type"], info["message_id"], tag.json())


async def get_message_tag(info: MessageInfo) -> Tag | None:
    cache = await get_cache(info["type"], info["message_id"])
    return parse_raw_as(Tag, cache) if cache else None
