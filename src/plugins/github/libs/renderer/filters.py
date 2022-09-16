#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:07:50
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-16 17:11:07
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime, timezone

import humanize
from markdown_it import MarkdownIt
from githubkit.rest import GitHubRestModel, TimelineReviewedEvent

title_md = MarkdownIt("zero").enable("backticks")


def markdown_title(text: str) -> str:
    return title_md.renderInline(text)


def relative_time(value: datetime) -> str:
    if not value.tzinfo:
        value = value.replace(tzinfo=timezone.utc)
    now = datetime.now(value.tzinfo)
    delta = now - value
    if delta.microseconds > 0 and delta.days < 30:
        return humanize.naturaltime(delta)

    t = "%d %b" if value.year == now.year else "%d %b %Y"
    return f"on {humanize.naturalday(value, t)}"


def review_state(value: str) -> str:
    states = {
        "approved": "approved these changes",
        "changes_requested": "requested changes",
        "commented": "reviewed",
        "dismissed": "reviewed",
    }
    return states.get(value, value)


async def find_dismissed_review(
    past_timeline: list[GitHubRestModel], review_id: int
) -> TimelineReviewedEvent | None:
    for event in past_timeline:
        if isinstance(event, TimelineReviewedEvent) and event.id == review_id:
            return event
