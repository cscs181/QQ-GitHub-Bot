"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-18 17:21:33
@Description    : GitHub image renderer
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"


from githubkit import rest, webhooks
from nonebot.adapters.github import OAuthBot, GitHubBot

from src.plugins.github import config
from src.providers.playwright import content_screenshot

from .render import (
    issue_to_html,
    pr_diff_to_html,
    issue_closed_to_html,
    issue_opened_to_html,
    issue_commented_to_html,
)


async def issue_to_image(
    bot: GitHubBot | OAuthBot,
    issue: rest.Issue,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github issue/pr timeline to image"""
    html = await issue_to_html(bot, issue, config.github_theme)
    return await content_screenshot(html, width, height)


async def pr_diff_to_image(
    bot: GitHubBot | OAuthBot,
    issue: rest.Issue,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render a github pr diff to image"""
    html = await pr_diff_to_html(bot, issue, config.github_theme)
    return await content_screenshot(html, width, height)


async def issue_opened_to_image(
    bot: GitHubBot | OAuthBot,
    repo: webhooks.Repository,
    issue: webhooks.IssuesOpenedPropIssue | webhooks.PullRequestOpenedPropPullRequest,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render webhook event issue/opened to image"""
    html = await issue_opened_to_html(bot, repo, issue, config.github_theme)
    return await content_screenshot(html, width, height)


async def issue_commented_to_image(
    bot: GitHubBot | OAuthBot,
    repo: webhooks.Repository,
    issue: webhooks.IssueCommentCreatedPropIssue,
    comment: webhooks.IssueComment,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render webhook event issue_comment/created to image"""
    html = await issue_commented_to_html(bot, repo, issue, comment, config.github_theme)
    return await content_screenshot(html, width, height)


async def issue_closed_to_image(
    bot: GitHubBot | OAuthBot,
    repo: webhooks.Repository,
    issue: webhooks.IssuesClosedPropIssue | webhooks.PullRequestClosedPropPullRequest,
    width: int = 800,
    height: int = 300,
) -> bytes:
    """Render webhook event issue/closed to image"""
    html = await issue_closed_to_html(bot, repo, issue, config.github_theme)
    return await content_screenshot(html, width, height)
