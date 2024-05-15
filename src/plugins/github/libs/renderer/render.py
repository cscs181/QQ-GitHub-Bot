"""
@Author         : yanyongyu
@Date           : 2021-05-14 17:09:12
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-16 00:35:37
@Description    : GitHub html renderer
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from pathlib import Path
from typing import Literal

import jinja2
from githubkit.versions.latest import models
from nonebot.adapters.github import OAuthBot, GitHubBot

from .globals import scale_linear
from .context import DiffContext, IssueContext, ReadmeContext
from .filters import (
    debug_event,
    markdown_gfm,
    review_state,
    left_truncate,
    relative_time,
    markdown_emoji,
    markdown_title,
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
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssuesOpenedPropIssue | models.PullRequestWebhook,
    theme: Literal["light", "dark"] = "light",
) -> str:
    """Render issue or pr opened webhook event to html

    Args:
        repo: the webhook repository object
        issue: the webhook issue object
        theme: the theme of the html
    """
    template = env.get_template("views/issue-opened.html.jinja")
    return await template.render_async(repo=repo, issue=issue, theme=theme)


async def issue_commented_to_html(
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssueCommentCreatedPropIssue,
    comment: models.WebhookIssueCommentCreatedPropComment,
    theme: Literal["light", "dark"] = "light",
) -> str:
    """Render issue commented webhook event to html

    Args:
        repo: the webhook repository object
        issue: the webhook issue object
        comment: the webhook issue comment object
        theme: the theme of the html
    """
    template = env.get_template("views/issue-commented.html.jinja")
    return await template.render_async(
        repo=repo,
        issue=issue,
        comment=comment,
        highlight_comment=comment.id,
        theme=theme,
    )


async def issue_closed_to_html(
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssuesClosedPropIssue | models.PullRequestWebhook,
    theme: Literal["light", "dark"] = "light",
) -> str:
    """Render issue or pr closed webhook event to html

    Args:
        repo: the webhook repository object
        issue: the webhook issue object
        theme: the theme of the html
    """
    # 直接用issue-opened.html.jinja感觉就行
    template = env.get_template("views/issue-opened.html.jinja")
    return await template.render_async(repo=repo, issue=issue, theme=theme)
