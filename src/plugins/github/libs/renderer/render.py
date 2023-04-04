#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-05-14 17:09:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-04-05 01:02:54
@Description    : GitHub html renderer
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path
from typing import Literal

import jinja2
from githubkit import rest, webhooks

from .filters import (
    debug_event,
    markdown_gfm,
    review_state,
    left_truncate,
    relative_time,
    markdown_emoji,
    markdown_title,
)
from .globals import (
    REACTION_EMOJIS,
    scale_linear,
    get_issue_repo,
    get_pull_request,
    get_issue_timeline,
    find_dismissed_review,
    get_comment_reactions,
    get_issue_label_color,
    get_pull_request_diff,
)

env = jinja2.Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
    enable_async=True,
)
"""Jinja environment for rendering"""

env.filters["markdown_title"] = markdown_title
env.filters["markdown_emoji"] = markdown_emoji
env.filters["markdown_gfm"] = markdown_gfm
env.filters["relative_time"] = relative_time
env.filters["debug_event"] = debug_event
env.filters["review_state"] = review_state
env.filters["left_truncate"] = left_truncate

env.globals["get_issue_repo"] = get_issue_repo
env.globals["get_issue_timeline"] = get_issue_timeline
env.globals["get_pull_request"] = get_pull_request
env.globals["get_pull_request_diff"] = get_pull_request_diff
env.globals["get_comment_reactions"] = get_comment_reactions
env.globals["REACTION_EMOJIS"] = REACTION_EMOJIS
env.globals["get_issue_label_color"] = get_issue_label_color
env.globals["find_dismissed_review"] = find_dismissed_review
env.globals["scale_linear"] = scale_linear


async def issue_to_html(
    issue: rest.Issue, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render issue or pr with timeline to html

    Args:
        issue: the issue object
        theme: the theme of the html
    """
    template = env.get_template("views/issue.html.jinja")
    return await template.render_async(issue=issue, theme=theme)


async def pr_diff_to_html(
    issue: rest.Issue, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render pr diff to html

    Args:
        issue: the issue object of the pr
        theme: the theme of the html
    """
    template = env.get_template("views/diff.html.jinja")
    return await template.render_async(issue=issue, theme=theme)


async def issue_opened_to_html(
    repo: webhooks.Repository,
    issue: webhooks.IssuesOpenedPropIssue,
    theme: Literal["light", "dark"] = "light",
) -> str:
    """Render issue or pr with timeline to html

    Args:
        repo: the webhook repository object
        issue: the webhook issue object
        theme: the theme of the html
    """
    template = env.get_template("views/issue-opened.html.jinja")
    return await template.render_async(repo=repo, issue=issue, theme=theme)
