#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-05-14 00:57:33
@LastEditors    : yanyongyu
@LastEditTime   : 2021-08-20 00:46:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime
from typing import List, Optional
from typing_extensions import Literal

from pydantic import BaseModel as _BaseModel, Field

from . import BaseModel

from .user import User, Actor


# Base Timeline Event
class TimelineEvent(BaseModel):
    event: str


# Commit Timeline Event
class TimelineEventCommitedUser(_BaseModel):
    name: str
    email: str
    date: datetime


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
    signature: Optional[str]
    payload: Optional[str]


class TimelineEventCommited(TimelineEvent):
    event: Literal["committed"]
    node_id: str
    sha: str
    url: str
    html_url: str
    author: TimelineEventCommitedUser
    committer: TimelineEventCommitedUser
    tree: TimelineEventCommitedTree
    message: str
    parents: List[TimelineEventCommitedCommit]
    verification: TimelineEventCommitedVerification


# Force Push
class TimelineEventForcePushed(TimelineEvent):
    event: Literal["head_ref_force_pushed"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Head Ref Deleted
class TimelineEventHeadDeleted(TimelineEvent):
    event: Literal["head_ref_deleted"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Issue Referenced
class TimelineEventReferenced(TimelineEvent):
    event: Literal["referenced"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: str
    commit_url: str
    created_at: datetime


# Issue Commented
class TimelineEventCommented(TimelineEvent):
    event: Literal["commented"]
    id: int
    node_id: str
    url: str
    html_url: str
    issue_url: str
    user: Actor
    created_at: datetime
    updated_at: datetime
    author_association: str
    body: str
    body_text: Optional[str]
    body_html: Optional[str]
    actor: Actor


# Issue Comment Deleted
class TimelineEventCommentDeleted(TimelineEvent):
    event: Literal["comment_deleted"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Issue Mentioned Person
class TimelineEventMentioned(TimelineEvent):
    event: Literal["mentioned"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Person Subscribed/Unsubscribed Issue
class TimelineEventSubscribed(TimelineEvent):
    event: Literal["subscribed"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


class TimelineEventUnsubscribed(TimelineEvent):
    event: Literal["unsubscribed"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Pull Request Reviewed
class TimelineEventReviewedLink(_BaseModel):
    href: str


class TimelineEventReviewedLinks(_BaseModel):
    html: TimelineEventReviewedLink
    pull_request: TimelineEventReviewedLink


class TimelineEventReviewed(TimelineEvent):
    event: Literal["reviewed"]
    id: int
    node_id: str
    user: User
    state: str
    html_url: str
    commit_id: str
    pull_request_url: str
    author_association: str
    submitted_at: datetime
    body: Optional[str]
    body_text: Optional[str]
    body_html: Optional[str]
    links: TimelineEventReviewedLinks = Field(alias="_links")


# Pull Request Review Requested
class TimelineEventReviewRequested(TimelineEvent):
    event: Literal["review_requested"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    review_requester: User
    requested_reviewer: User


# Pull Request Review Removed
class TimelineEventReviewRemoved(TimelineEvent):
    event: Literal["review_request_removed"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    review_requester: User
    requested_reviewer: User


# Pull Request Review Dismissed
class TimelineEventReviewDismissedInfo(_BaseModel):
    state: str
    review_id: int
    dismissal_message: Optional[str]
    dismissal_commit_id: Optional[str]


class TimelineEventReviewDismissed(TimelineEvent):
    event: Literal["review_dismissed"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    dismissed_review: TimelineEventReviewDismissedInfo


# Issue Title Renamed
class TimelineEventRenamedDetail(_BaseModel):
    to: str
    from_: str = Field(alias="from")


class TimelineEventRenamed(TimelineEvent):
    event: Literal["renamed"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    rename: TimelineEventRenamedDetail


# Issue Labeled/Unlabeled
class TimelineEventLabelInfo(_BaseModel):
    name: str
    color: str


class TimelineEventLabeled(TimelineEvent):
    event: Literal["labeled"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    label: TimelineEventLabelInfo


class TimelineEventUnlabeled(TimelineEvent):
    event: Literal["unlabeled"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    label: TimelineEventLabelInfo


# Pull Request Merged
class TimelineEventMerged(TimelineEvent):
    event: Literal["merged"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: str
    commit_url: str
    created_at: datetime


# Issue Closed
class TimelineEventClosed(TimelineEvent):
    event: Literal["closed"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Issue Added to Project
class TimelineEventAddedToProject(TimelineEvent):
    event: Literal["added_to_project"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Issue Moved Columns in Project
class TimelineEventMovedColumnsInProject(TimelineEvent):
    event: Literal["moved_columns_in_project"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Issue Removed from Project
class TimelineEventRemovedFromProject(TimelineEvent):
    event: Literal["removed_from_project"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime


# Issue Added to/Removed from Milestone
class TimelineEventMilestonedDetail(_BaseModel):
    title: str


class TimelineEventMilestoned(TimelineEvent):
    event: Literal["milestoned"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    milestone: TimelineEventMilestonedDetail


class TimelineEventDemilestoned(TimelineEvent):
    event: Literal["demilestoned"]
    id: int
    node_id: str
    url: str
    actor: Actor
    commit_id: Optional[str]
    commit_url: Optional[str]
    created_at: datetime
    milestone: TimelineEventMilestonedDetail


# TODO: other events
