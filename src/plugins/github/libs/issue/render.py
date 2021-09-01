#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-05-14 17:09:12
@LastEditors    : yanyongyu
@LastEditTime   : 2021-09-02 01:27:11
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path
from inspect import isclass
from datetime import datetime
from typing import Any, Optional

import jinja2
import humanize
from unidiff import PatchSet
from nonebot.log import logger

from src.libs.github.models import Issue, PaginatedList
from src.libs.github.models.timeline import TimelineEvent, TimelineEventReviewed

env = jinja2.Environment(extensions=["jinja2.ext.loopcontrols"],
                         loader=jinja2.FileSystemLoader(
                             Path(__file__).parent / "templates"),
                         enable_async=True)


def classname(value: Any) -> str:
    return value.__name__ if isclass(value) else type(value).__name__


def relative_time(value: datetime):
    return humanize.naturaltime(datetime.now(value.tzinfo) - value)


def review_state(value: str) -> str:
    states = {
        "approved": "approved these changes",
        "changes_requested": "requested changes",
        "commented": "reviewed",
        "dismissed": "reviewed"
    }
    return states.get(value, value)


def debug_event(event: TimelineEvent):
    # not sub class of TimelineEvent
    if type(event) is TimelineEvent:
        # event not passed process
        logger.error(f"Unhandled event type: {event.event}", event=event.dict())
    # ignore other event types
    return ""


@jinja2.pass_context
async def find_dismissed_review(
        ctx: jinja2.runtime.Context,
        review_id: int) -> Optional[TimelineEventReviewed]:
    timeline: Optional[PaginatedList[TimelineEvent]] = ctx.get("timeline", None)
    if not timeline:
        return

    async for event in timeline:
        if getattr(event, "id", None) == review_id:
            return event if isinstance(event, TimelineEventReviewed) else None


env.filters["classname"] = classname
env.filters["relative_time"] = relative_time
env.filters["review_state"] = review_state
env.filters["debug_event"] = debug_event
env.filters["find_dismissed_review"] = find_dismissed_review


#! FIXME
# pr status merged can only be found in timeline events
# or using api: `/repos/{owner}/{repo}/pulls/{pull_number}/merge`
async def issue_to_html(owner: str, repo_name: str, issue: Issue) -> str:
    template = env.get_template("issue.html")
    async with issue:
        timeline = await issue.get_timeline()
        return await template.render_async(owner=owner,
                                           repo_name=repo_name,
                                           issue=issue,
                                           timeline=timeline)


async def pr_diff_to_html(owner: str, repo_name: str, issue: Issue) -> str:
    template = env.get_template("diff.html")
    async with issue:
        diff = await issue.get_diff()
        return await template.render_async(owner=owner,
                                           repo_name=repo_name,
                                           issue=issue,
                                           diff=PatchSet(diff))
