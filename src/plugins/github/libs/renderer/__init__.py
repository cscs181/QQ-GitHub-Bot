"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : yanyongyu
@LastEditTime   : 2024-06-10 12:15:55
@Description    : GitHub image renderer
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from datetime import date
from hashlib import sha256

from pydantic_core import to_json
from githubkit.versions.latest import models
from playwright.async_api import Route, Request
from nonebot.adapters.github import OAuthBot, GitHubBot

from src.plugins.github import config
from src.providers.playwright import get_new_page
from src.plugins.github.cache.rendered_image import (
    get_rendered_image,
    save_rendered_image,
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
from .render import (
    issue_to_html,
    readme_to_html,
    pr_diff_to_html,
    issue_closed_to_html,
    issue_opened_to_html,
    issue_commented_to_html,
    user_contribution_to_html,
)

WIDTH = 800
HEIGHT = 30


async def _github_html_to_image(html: str, context_url: str | None = None) -> bytes:
    async def _intercept_network_request(route: Route, request: Request):
        if context_url and request.url == context_url:
            await route.fulfill(status=200, body=html, content_type="text/html")
            return
        await route.continue_()

    async with get_new_page(viewport={"width": WIDTH, "height": HEIGHT}) as page:
        if context_url:
            await page.route(lambda url: url == context_url, _intercept_network_request)
            await page.goto(context_url)
        else:
            await page.set_content(html)

        # expand all details
        await page.evaluate(
            "() => document.querySelectorAll('details').forEach(e => e.open = true)"
        )
        return await page.screenshot(timeout=60_000, full_page=True)


def _context_hash(
    context: (
        UserContributionContext
        | ReadmeContext
        | IssueContext
        | DiffContext
        | IssueOpenedContext
        | IssueCommentedContext
        | IssueClosedContext
    ),
) -> str:
    context_json = to_json(context)
    return sha256(context_json).hexdigest()


async def user_contribution_to_image(
    username: str,
    user_avatar: str,
    total_contributions: int,
    total_commit_contributions: int,
    total_issue_contributions: int,
    total_pull_request_contributions: int,
    total_pull_request_review_contributions: int,
    weeks: list[list[tuple[str, date]]],
) -> bytes:
    """Render user contribution calendar to image"""
    context = UserContributionContext.from_user_contribution(
        username,
        user_avatar,
        total_contributions,
        total_commit_contributions,
        total_issue_contributions,
        total_pull_request_contributions,
        total_pull_request_review_contributions,
        weeks,
    )
    context_hash = _context_hash(context)
    if cached_image := await get_rendered_image("contribution", context_hash):
        return cached_image

    html = await user_contribution_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    await save_rendered_image("contribution", context_hash, image)
    return image


async def readme_to_image(
    bot: GitHubBot | OAuthBot, repo: models.FullRepository, readme: str
) -> bytes:
    """Render a github issue/pr timeline to image"""
    context = await ReadmeContext.from_repo_readme(bot, repo, readme)
    context_hash = _context_hash(context)
    if cached_image := await get_rendered_image("readme", context_hash):
        return cached_image

    html = await readme_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(
        html,
        f"https://raw.githubusercontent.com/{repo.owner.login}/{repo.name}/{repo.default_branch}/",
    )
    await save_rendered_image("readme", context_hash, image)
    return image


async def issue_to_image(
    bot: GitHubBot | OAuthBot, issue: models.Issue, highlight_comment: int | None = None
) -> bytes:
    """Render a github issue/pr timeline to image"""
    context = await IssueContext.from_issue(bot, issue, highlight_comment)
    context_hash = _context_hash(context)
    if cached_image := await get_rendered_image("issue", context_hash):
        return cached_image

    html = await issue_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    await save_rendered_image("issue", context_hash, image)
    return image


async def pr_diff_to_image(bot: GitHubBot | OAuthBot, issue: models.Issue) -> bytes:
    """Render a github pr diff to image"""
    context = await DiffContext.from_issue(bot, issue)
    context_hash = _context_hash(context)
    if cached_image := await get_rendered_image("diff", context_hash):
        return cached_image

    html = await pr_diff_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    await save_rendered_image("diff", context_hash, image)
    return image


async def issue_opened_to_image(
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssuesOpenedPropIssue | models.PullRequestWebhook,
) -> bytes:
    """Render webhook event issue/opened to image"""
    context = await IssueOpenedContext.from_webhook(bot, repo, issue)
    context_hash = _context_hash(context)
    if cached_image := await get_rendered_image("issue_opened", context_hash):
        return cached_image

    html = await issue_opened_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    await save_rendered_image("issue_opened", context_hash, image)
    return image


async def issue_commented_to_image(
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssueCommentCreatedPropIssue,
    comment: models.WebhookIssueCommentCreatedPropComment,
) -> bytes:
    """Render webhook event issue_comment/created to image"""
    context = await IssueCommentedContext.from_webhook(bot, repo, issue, comment)
    context_hash = _context_hash(context)
    if cached_image := await get_rendered_image("issue_commented", context_hash):
        return cached_image

    html = await issue_commented_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    await save_rendered_image("issue_commented", context_hash, image)
    return image


async def issue_closed_to_image(
    bot: GitHubBot | OAuthBot,
    repo: models.RepositoryWebhooks,
    issue: models.WebhookIssuesClosedPropIssue | models.PullRequestWebhook,
    sender: models.SimpleUserWebhooks,
) -> bytes:
    """Render webhook event issue/closed to image"""
    context = await IssueClosedContext.from_webhook(bot, repo, issue, sender)
    context_hash = _context_hash(context)
    if cached_image := await get_rendered_image("issue_closed", context_hash):
        return cached_image

    html = await issue_closed_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    await save_rendered_image("issue_closed", context_hash, image)
    return image
