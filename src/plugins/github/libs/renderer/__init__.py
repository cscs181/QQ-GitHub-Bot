"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-16 15:20:23
@Description    : GitHub image renderer
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from githubkit.versions.latest import models
from nonebot.adapters.github import OAuthBot, GitHubBot

from src.plugins.github import config
from src.providers.playwright import content_screenshot

from .context import (
    DiffContext,
    IssueContext,
    ReadmeContext,
    IssueClosedContext,
    IssueOpenedContext,
    IssueCommentedContext,
)
from .render import (
    issue_to_html,
    readme_to_html,
    pr_diff_to_html,
    issue_closed_to_html,
    issue_opened_to_html,
    issue_commented_to_html,
)


async def readme_to_image(
    bot: GitHubBot | OAuthBot,
    repo: models.FullRepository,
    readme: str,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github issue/pr timeline to image"""
    context = await ReadmeContext.from_repo_readme(bot, repo, readme)
    html = await readme_to_html(context, theme=config.github_theme)
    return await content_screenshot(html, width, height)


async def issue_to_image(
    bot: GitHubBot | OAuthBot,
    issue: models.Issue,
    highlight_comment: int | None = None,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github issue/pr timeline to image"""
    context = await IssueContext.from_issue(bot, issue, highlight_comment)
    html = await issue_to_html(context, theme=config.github_theme)
    return await content_screenshot(html, width, height)


async def pr_diff_to_image(
    bot: GitHubBot | OAuthBot,
    issue: models.Issue,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github pr diff to image"""
    context = await DiffContext.from_issue(bot, issue)
    html = await pr_diff_to_html(context, theme=config.github_theme)
    return await content_screenshot(html, width, height)


async def issue_opened_to_image(
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssuesOpenedPropIssue | models.PullRequestWebhook,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render webhook event issue/opened to image"""
    context = await IssueOpenedContext.from_webhook(bot, repo, issue)
    html = await issue_opened_to_html(context, theme=config.github_theme)
    return await content_screenshot(html, width, height)


async def issue_commented_to_image(
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssueCommentCreatedPropIssue,
    comment: models.WebhookIssueCommentCreatedPropComment,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render webhook event issue_comment/created to image"""
    context = await IssueCommentedContext.from_webhook(bot, repo, issue, comment)
    html = await issue_commented_to_html(context, theme=config.github_theme)
    return await content_screenshot(html, width, height)


async def issue_closed_to_image(
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssuesClosedPropIssue | models.PullRequestWebhook,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render webhook event issue/closed to image"""
    context = await IssueClosedContext.from_webhook(bot, repo, issue)
    html = await issue_closed_to_html(context, theme=config.github_theme)
    return await content_screenshot(html, width, height)
