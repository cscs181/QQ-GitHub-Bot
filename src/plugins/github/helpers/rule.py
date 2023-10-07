"""
@Author         : yanyongyu
@Date           : 2022-10-27 04:24:58
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-06 17:10:56
@Description    : Rule helpers
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.rule import Rule
from nonebot.adapters import Event
from nonebot.adapters.github import Event as GitHubEvent


async def no_github_event(event: Event):
    """Check if the event is not a github webhook event"""
    return not isinstance(event, GitHubEvent)


NO_GITHUB_EVENT = Rule(no_github_event)
