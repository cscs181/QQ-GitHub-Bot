#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 16:57:04
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-12 14:57:52
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime
from typing import List, Optional

from . import BaseModel

from .user import User
from .label import Label
from .issue_pull_request import IssuePullRequest


class Issue(BaseModel):
    id: int
    node_id: str
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    number: int
    state: str
    title: str
    body: str
    body_text: str
    body_html: str
    user: User
    labels: List[Label]
    assignee: Optional[User]
    assignees: List[User]
    # milestone: Optional[Milestone]
    locked: bool
    active_lock_reason: Optional[str]
    comments: int
    pull_request: Optional[IssuePullRequest]
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    closed_by: Optional[User]
    author_association: str

    @property
    def is_pull_request(self) -> bool:
        return bool(self.pull_request)
