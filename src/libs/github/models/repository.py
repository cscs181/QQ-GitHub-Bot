#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 01:33:54
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-11 16:57:40
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime
from typing_extensions import Literal
from typing import List, Union, Optional

from . import BaseModel

from .user import User
from .issue import Issue
from .license import License
from .permissions import Permissions
from .organization import Organization


class LazyRepository(BaseModel):
    full_name: str

    async def get_issue(self, number: int):
        response = await self._requester.request(
            "GET", f"/repos/{self.full_name}/issues/{number}")
        return Issue.parse_obj(response.json())

    # FIXME: pass a milestone object, assignee user object
    async def get_issues(self,
                         milestone: Optional[Union[int,
                                                   Literal["*",
                                                           "none"]]] = None,
                         state: Optional[Literal["open", "closed",
                                                 "all"]] = None,
                         assignee: Optional[Union[str, Literal["*",
                                                               "none"]]] = None,
                         creator: Optional[str] = None,
                         mentioned: Optional[str] = None,
                         labels: Optional[List[str]] = None,
                         sort: Optional[Literal["created", "updated",
                                                "comments"]] = None,
                         direction: Optional[Literal["asc", "desc"]] = None,
                         since: Optional[datetime] = None):
        params = {}
        if milestone:
            params["milestone"] = milestone
        if state:
            params["state"] = state
        if assignee:
            params["assignee"] = assignee
        if creator:
            params["creator"] = creator
        if mentioned:
            params["mentioned"] = mentioned
        if labels:
            params["labels"] = ",".join(labels)
        if sort:
            params["sort"] = sort
        if direction:
            params["direction"] = direction
        if since:
            params["since"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")


class Repository(LazyRepository):
    """
    https://docs.github.com/en/rest/reference/repos
    """
    id: int
    node_id: str
    name: str
    owner: Union[User, Organization]
    private: bool
    html_url: str
    description: str
    fork: bool
    url: str
    archive_url: str
    assignees_url: str
    blobs_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str
    deployments_url: str
    downloads_url: str
    events_url: str
    forks_url: str
    git_commits_url: str
    git_refs_url: str
    git_tags_url: str
    git_url: str
    issue_comment_url: str
    issue_events_url: str
    issues_url: str
    keys_url: str
    labels_url: str
    languages_url: str
    merges_url: str
    milestones_url: str
    notifications_url: str
    pulls_url: str
    releases_url: str
    ssh_url: str
    stargazers_url: str
    statuses_url: str
    subscribers_url: str
    subscription_url: str
    tags_url: str
    teams_url: str
    trees_url: str
    clone_url: str
    mirror_url: Optional[str]
    hooks_url: str
    svn_url: str
    homepage: str
    language: Optional[str]
    forks_count: int
    forks: int
    stargazers_count: int
    watchers_count: int
    watchers: int
    size: int
    default_branch: str
    open_issues_count: int
    open_issues: int
    is_template: Optional[bool] = None
    topics: Optional[List[str]] = None
    has_issues: bool
    has_projects: bool
    has_wiki: bool
    has_pages: bool
    has_downloads: bool
    archived: bool
    disabled: bool
    visibility: Optional[str] = None
    pushed_at: datetime
    created_at: datetime
    updated_at: datetime
    permissions: Optional[Permissions] = None
    allow_rebase_merge: Optional[bool] = None
    template_repository: Optional["Repository"] = None
    temp_clone_token: Optional[str]
    allow_squash_merge: Optional[bool] = None
    delete_branch_on_merge: Optional[bool] = None
    allow_merge_commit: Optional[bool] = Optional[None]
    subscribers_count: int
    network_count: int
    license: Optional[License]
    organization: Optional[Organization] = None
    parent: Optional["Repository"] = None
    source: Optional["Repository"] = None
