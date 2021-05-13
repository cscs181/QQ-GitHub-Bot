#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-05-14 00:57:33
@LastEditors    : yanyongyu
@LastEditTime   : 2021-05-14 02:18:47
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel as _BaseModel, Field

from . import BaseModel

from .user import User


class TimelineEvent(BaseModel):
    node_id: str
    event: str


class TimelineEventCommitedUser(_BaseModel):
    name: str
    email: str
    data: datetime


class TimelineEventCommitedTree(_BaseModel):
    sha: str
    url: str


class TimelineEventCommitedCommit(_BaseModel):
    sha: str
    url: str
    html_url: str


class TimelineEventCommitedVerification(_BaseModel):
    verified: bool
    reason: str
    signature: str
    payload: str


class TimelineEventCommited(TimelineEvent):
    sha: str
    url: str
    html_url: str
    author: TimelineEventCommitedUser
    committer: TimelineEventCommitedUser
    tree: TimelineEventCommitedTree
    message: str
    parents: List[TimelineEventCommitedCommit]
    verification: TimelineEventCommitedVerification


class TimelineEventCommented(TimelineEvent):
    id: int
    url: str
    html_url: str
    issue_url: str
    user: User
    created_at: datetime
    updated_at: datetime
    author_association: str
    body: str
    body_text: Optional[str]
    body_html: Optional[str]
    performed_via_github_app: bool
    actor: User


class TimelineEventReviewedLink(_BaseModel):
    href: str


class TimelineEventReviewedLinks(_BaseModel):
    html: TimelineEventReviewedLink
    pull_request: TimelineEventReviewedLink


class TimelineEventReviewed(TimelineEvent):
    id: int
    user: User
    state: str
    html_url: str
    commit_id: str
    pull_request_url: str
    author_association: str
    submitted_at: datetime
    body: str
    body_text: Optional[str]
    body_html: Optional[str]
    links: TimelineEventReviewedLinks


class TimelineEventRenamedDetail(_BaseModel):
    to: str
    from_: str = Field(alias="from")

    class Config:
        allow_population_by_field_name = True


class TimelineEventRenamed(TimelineEvent):
    id: int
    url: str
    actor: User
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    rename: TimelineEventRenamedDetail
    performed_via_github_app: Optional[bool]
