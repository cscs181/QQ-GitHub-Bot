#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-09-12 00:35:57
@LastEditors    : yanyongyu
@LastEditTime   : 2021-09-12 01:47:10
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime
from typing import Any, List, Union, Optional

from pydantic import BaseModel as _BaseModel

from . import BaseModel
from .label import Label
from .user import User, Actor
from .repository import Repository


class PullRequestTeam(_BaseModel):
    id: int
    node_id: str
    url: str
    html_url: str
    name: str
    slug: str
    description: str
    privacy: str
    permission: str
    members_url: str
    repositories_url: str


class PullRequestCommit(_BaseModel):
    label: str
    ref: str
    sha: str
    user: Actor
    repo: Optional[Repository]


class PullRequest(BaseModel):
    id: int
    node_id: str
    url: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: User
    body: Optional[str]
    body_text: Optional[str]
    body_html: Optional[str]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    merged_at: Optional[datetime]
    merge_commit_sha: str
    assignee: Optional[User]
    assignees: List[User]
    requested_reviewers: List[User]
    requested_teams: List[PullRequestTeam]
    labels: List[Label]
    # milestone: Optional[Milestone]
    draft: bool
    commits_url: str
    review_comments_url: str
    review_comment_url: str
    comments_url: str
    statuses_url: str
    head: PullRequestCommit
    base: PullRequestCommit
    author_association: str
    # FIXME: what's this?
    auto_merge: Optional[Any]
    active_lock_reason: Optional[str]
    merged: bool
    mergeable: Optional[bool]
    rebaseable: Optional[bool]
    mergeable_state: str
    merged_by: Optional[User]
    comments: int
    review_comments: int
    maintainer_can_modify: bool
    commits: int
    additions: int
    deletions: int
    changed_files: int

    async def get_diff(self) -> str:
        response = await self.requester.request("GET", self.diff_url)
        return response.text
