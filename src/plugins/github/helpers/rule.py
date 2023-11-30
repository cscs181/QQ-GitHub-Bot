"""
@Author         : yanyongyu
@Date           : 2022-10-27 04:24:58
@LastEditors    : yanyongyu
@LastEditTime   : 2023-11-30 12:13:11
@Description    : Rule helpers
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot.rule import Rule
from nonebot.adapters import Event
from nonebot.adapters.github import Event as GitHubEvent

from src.plugins.github.dependencies import OPTIONAL_REPLY_TAG
from src.plugins.github.cache.message_tag import IssueTag, PullRequestTag
from src.providers.platform import OPTIONAL_GROUP_INFO, OPTIONAL_IS_PRIVATE


async def no_github_event(event: Event):
    """Check if the event is not a github webhook event"""
    return not isinstance(event, GitHubEvent)


NO_GITHUB_EVENT = Rule(no_github_event)


async def match_when_private(is_private: OPTIONAL_IS_PRIVATE) -> bool:
    return is_private is True


MATCH_WHEN_PRIVATE = Rule(match_when_private)


async def match_when_group(group_info: OPTIONAL_GROUP_INFO) -> bool:
    return group_info is not None


MATCH_WHEN_GROUP = Rule(match_when_group)


async def match_when_private_or_group(
    is_private: OPTIONAL_IS_PRIVATE, group_info: OPTIONAL_GROUP_INFO
) -> bool:
    return is_private is True or group_info is not None


MATCH_WHEN_PRIVATE_OR_GROUP = Rule(match_when_private_or_group)


async def reply_any(reply_tag: OPTIONAL_REPLY_TAG) -> bool:
    return reply_tag is not None


REPLY_ANY = Rule(reply_any)


async def reply_issue_or_pr(reply_tag: OPTIONAL_REPLY_TAG) -> bool:
    return isinstance(reply_tag, IssueTag | PullRequestTag)


REPLY_ISSUE_OR_PR = Rule(reply_issue_or_pr)


async def reply_pr(reply_tag: OPTIONAL_REPLY_TAG) -> bool:
    return isinstance(reply_tag, PullRequestTag)


REPLY_PR = Rule(reply_pr)
