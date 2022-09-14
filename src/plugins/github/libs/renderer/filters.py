#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:07:50
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 16:07:51
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime

import jinja2
import humanize
from githubkit.rest import GitHubRestModel, TimelineReviewedEvent


def relative_time(value: datetime):
    return humanize.naturaltime(datetime.now(value.tzinfo) - value)


def review_state(value: str) -> str:
    states = {
        "approved": "approved these changes",
        "changes_requested": "requested changes",
        "commented": "reviewed",
        "dismissed": "reviewed",
    }
    return states.get(value, value)


@jinja2.pass_context
async def find_dismissed_review(
    ctx: jinja2.runtime.Context, past_timeline: list[GitHubRestModel], review_id: int
) -> TimelineReviewedEvent | None:
    for event in past_timeline:
        if isinstance(event, TimelineReviewedEvent) and event.id == review_id:
            return event
