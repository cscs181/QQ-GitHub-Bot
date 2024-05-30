from colorsys import rgb_to_hls

from githubkit.versions.latest import models
from githubkit.exception import RequestFailed, RequestTimeout
from nonebot.adapters.github import (
    OAuthBot,
    GitHubBot,
    ActionFailed,
    NetworkError,
    ActionTimeout,
)

REACTION_EMOJIS = {
    "plus_one": "👍",
    "minus_one": "👎",
    "laugh": "😄",
    "confused": "😕",
    "hooray": "🎉",
    "heart": "❤️",
    "rocket": "🚀",
    "eyes": "👀",
}
"""Issue comment reaction emoji mapping"""


def get_comment_reactions(
    reactions: (
        models.ReactionRollup
        | models.WebhookIssuesOpenedPropIssuePropReactions
        | models.WebhookIssuesClosedPropIssueMergedReactions
        | models.WebhookIssueCommentCreatedPropIssueMergedReactions
        | models.WebhookIssueCommentEditedPropIssueMergedReactions
        | models.WebhookIssueCommentCreatedPropCommentPropReactions
        | models.WebhooksIssueCommentPropReactions
    ),
) -> dict[str, int]:
    """Parse the reactions of the issue comment"""
    result: dict[str, int] = {}
    for reaction, emoji in REACTION_EMOJIS.items():
        if count := getattr(reactions, reaction, None):
            result[emoji] = count
    return result


def get_issue_label_color(color: str) -> tuple[int, int, int, int, int, int]:
    """Get the color of the issue label in RGB and HLS"""
    color = color.removeprefix("#")
    r = int(color[:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    h, l, s = rgb_to_hls(r / 255, g / 255, b / 255)  # noqa: E741
    return r, g, b, int(h * 360), int(l * 100), int(s * 100)


async def get_repo_from_issue(
    bot: GitHubBot | OAuthBot, issue: models.Issue
) -> models.FullRepository:
    try:
        resp = await bot.github.arequest(
            "GET", issue.repository_url, response_model=models.FullRepository
        )
    except RequestFailed as e:
        raise ActionFailed(e.response) from None
    except RequestTimeout as e:
        raise ActionTimeout(e.request) from None
    except Exception as e:
        raise NetworkError(f"API request failed: {e!r}") from e

    return resp.parsed_data


async def get_pull_request_from_issue(
    bot: GitHubBot | OAuthBot,
    issue: (
        models.Issue
        | models.WebhookIssueCommentCreatedPropIssue
        | models.WebhookIssueCommentEditedPropIssue
    ),
) -> models.PullRequest | None:
    if issue.pull_request and issue.pull_request.url:
        try:
            resp = await bot.github.arequest(
                "GET", issue.pull_request.url, response_model=models.PullRequest
            )
        except RequestFailed as e:
            raise ActionFailed(e.response) from None
        except RequestTimeout as e:
            raise ActionTimeout(e.request) from None
        except Exception as e:
            raise NetworkError(f"API request failed: {e!r}") from e

        return resp.parsed_data
    return None


async def get_diff_from_pull_request(
    bot: GitHubBot | OAuthBot, pr: models.PullRequest
) -> str:
    try:
        resp = await bot.github.arequest("GET", pr.diff_url)
    except RequestFailed as e:
        raise ActionFailed(e.response) from None
    except RequestTimeout as e:
        raise ActionTimeout(e.request) from None
    except Exception as e:
        raise NetworkError(f"API request failed: {e!r}") from e
    return resp.text
