#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:07:50
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-26 15:08:33
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime, timezone

import humanize
from nonebot.log import logger
from markdown_it import MarkdownIt
from githubkit.rest import GitHubRestModel
from mdit_py_plugins.tasklists import tasklists_plugin

# FIXME: g-emoji in title
title_md = MarkdownIt("zero").enable("backticks")
gfm_md = MarkdownIt("gfm-like").use(tasklists_plugin)


def markdown_title(text: str) -> str:
    return title_md.renderInline(text)


def markdown_gfm(text: str) -> str:
    return gfm_md.render(text)


def relative_time(value: datetime | str) -> str:
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    if not value.tzinfo:
        value = value.replace(tzinfo=timezone.utc)
    now = datetime.now(value.tzinfo)
    delta = now - value
    if delta.microseconds > 0 and delta.days < 30:
        return humanize.naturaltime(delta)

    t = "%d %b" if value.year == now.year else "%d %b %Y"
    return f"on {humanize.naturalday(value, t)}"


def debug_event(event: GitHubRestModel) -> str:
    logger.debug(f"Unhandled event: {event.dict()}")
    logger.error(
        f"Unhandled event type: {event.__class__.__name__}",
        event=event.dict(),
    )
    return ""


def review_state(value: str) -> str:
    states = {
        "approved": "approved these changes",
        "changes_requested": "requested changes",
        "commented": "reviewed",
        "dismissed": "reviewed",
    }
    return states.get(value, value)
