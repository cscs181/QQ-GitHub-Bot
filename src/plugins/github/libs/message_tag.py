#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-13 15:59:44
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-13 16:02:54
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Literal, Annotated

from pydantic import Field, BaseModel

from src.plugins.github.cache import get_message_tag, create_message_tag


class RepoTag(BaseModel):
    type: Literal["repo"]
    owner: str
    repo: str


class IssueTag(BaseModel):
    type: Literal["issue"]
    issue_number: int


class PullRequestTag(BaseModel):
    type: Literal["pull_request"]
    pull_request_number: int


Tag = Annotated[RepoTag | IssueTag | PullRequestTag, Field(discriminator="type")]
