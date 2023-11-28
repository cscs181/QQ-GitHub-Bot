"""
@Author         : yanyongyu
@Date           : 2021-05-14 17:09:12
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-28 15:31:22
@Description    : GitHub html renderer
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from pathlib import Path
from typing import Literal

import jinja2
from githubkit import rest, webhooks
from nonebot.adapters.github import OAuthBot, GitHubBot

from .context import set_context_bot
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
    bot: GitHubBot | OAuthBot,
    issue: rest.Issue,
    highlight_comment: int | None = None,
    theme: Literal["light", "dark"] = "light",
) -> str:
    """Render issue or pr with timeline to html

    Args:
        issue: the issue object
        theme: the theme of the html
    """
    template = env.get_template("views/issue.html.jinja")
    with set_context_bot(bot):
        return await template.render_async(
            issue=issue, highlight_comment=highlight_comment, theme=theme
        )


async def pr_diff_to_html(
    bot: GitHubBot | OAuthBot,
    issue: rest.Issue,
    theme: Literal["light", "dark"] = "light",
) -> str:
    """Render pr diff to html

    Args:
        issue: the issue object of the pr
        theme: the theme of the html
    """
    template = env.get_template("views/diff.html.jinja")
    with set_context_bot(bot):
        return await template.render_async(issue=issue, theme=theme)


async def issue_opened_to_html(
    bot: GitHubBot | OAuthBot,
    repo: webhooks.Repository,
    issue: webhooks.IssuesOpenedPropIssue | webhooks.PullRequestOpenedPropPullRequest,
    theme: Literal["light", "dark"] = "light",
) -> str:
    """Render issue or pr opened webhook event to html

    Args:
        repo: the webhook repository object
        issue: the webhook issue object
        theme: the theme of the html
    """
    template = env.get_template("views/issue-opened.html.jinja")
    with set_context_bot(bot):
        return await template.render_async(repo=repo, issue=issue, theme=theme)


async def issue_commented_to_html(
    bot: GitHubBot | OAuthBot,
    repo: webhooks.Repository,
    issue: webhooks.IssueCommentCreatedPropIssue,
    comment: webhooks.IssueComment,
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
    with set_context_bot(bot):
        return await template.render_async(
            repo=repo,
            issue=issue,
            comment=comment,
            highlight_comment=comment.id,
            theme=theme,
        )


async def issue_closed_to_html(
    bot: GitHubBot | OAuthBot,
    repo: webhooks.Repository,
    issue: webhooks.IssuesClosedPropIssue | webhooks.PullRequestClosedPropPullRequest,
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
    with set_context_bot(bot):
        return await template.render_async(repo=repo, issue=issue, theme=theme)
