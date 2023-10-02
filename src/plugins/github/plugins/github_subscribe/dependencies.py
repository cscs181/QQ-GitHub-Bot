"""
@Author         : yanyongyu
@Date           : 2022-10-26 15:35:46
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-27 09:29:05
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.adapters import Event
from nonebot.matcher import Matcher

from src.plugins.github.helpers import get_user_info, get_group_info
from src.plugins.github.models import UserSubscription, GroupSubscription
from src.plugins.github.libs.platform import (
    list_user_subscriptions,
    list_group_subscriptions,
)


async def bypass_create(matcher: Matcher) -> None:
    if matcher.get_arg("full_name") is not None:
        matcher.skip()


async def list_user(event: Event) -> list[UserSubscription]:
    if info := get_user_info(event):
        return await list_user_subscriptions(info)
    return []


async def list_group(event: Event) -> list[GroupSubscription]:
    if info := get_group_info(event):
        return await list_group_subscriptions(info)
    return []
