"""
@Author         : yanyongyu
@Date           : 2021-05-14 17:09:12
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-31 11:22:49
@Description    : GitHub html renderer
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from pathlib import Path
from typing import Literal

import jinja2

from .globals import scale_linear
from .filters import (
    debug_event,
    markdown_gfm,
    review_state,
    left_truncate,
    relative_time,
    markdown_emoji,
    markdown_title,
)
from .context import (
    DiffContext,
    IssueContext,
    ReadmeContext,
    IssueClosedContext,
    IssueOpenedContext,
    IssueCommentedContext,
    UserContributionContext,
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

env.globals["scale_linear"] = scale_linear


async def user_contribution_to_html(
    ctx: UserContributionContext, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render user contribution to image

    Args:
        ctx: the user contribution context
        theme: the theme of the image
    """
    template = env.get_template("views/contribution.html.jinja")
    return await template.render_async(ctx=ctx, theme=theme)


async def readme_to_html(
    ctx: ReadmeContext, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render repo readme to html

    Args:
        ctx: the readme context
        theme: the theme of the html
    """
    template = env.get_template("views/readme.html.jinja")
    return await template.render_async(ctx=ctx, theme=theme)


async def issue_to_html(
    ctx: IssueContext, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render issue or pr with timeline to html

    Args:
        ctx: the issue context
        theme: the theme of the html
    """
    template = env.get_template("views/issue.html.jinja")
    return await template.render_async(ctx=ctx, theme=theme)


async def pr_diff_to_html(
    ctx: DiffContext, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render pr diff to html

    Args:
        ctx: the pr diff context
        theme: the theme of the html
    """
    template = env.get_template("views/diff.html.jinja")
    return await template.render_async(ctx=ctx, theme=theme)


async def issue_opened_to_html(
    ctx: IssueOpenedContext, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render issue or pr opened webhook event to html

    Args:
        ctx: the issue opened context
        theme: the theme of the html
    """
    template = env.get_template("views/issue-opened.html.jinja")
    return await template.render_async(ctx=ctx, theme=theme)


async def issue_commented_to_html(
    ctx: IssueCommentedContext, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render issue commented webhook event to html

    Args:
        ctx: the issue commented context
        theme: the theme of the html
    """
    template = env.get_template("views/issue-commented.html.jinja")
    return await template.render_async(ctx=ctx, theme=theme)


async def issue_closed_to_html(
    ctx: IssueClosedContext, theme: Literal["light", "dark"] = "light"
) -> str:
    """Render issue or pr closed webhook event to html

    Args:
        ctx: the issue closed context
        theme: the theme of the html
    """
    template = env.get_template("views/issue-closed.html.jinja")
    return await template.render_async(ctx=ctx, theme=theme)
