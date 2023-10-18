"""
@Author         : yanyongyu
@Date           : 2023-10-08 16:15:02
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 16:25:55
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from typing import Annotated, TypeAlias

from nonebot.params import Depends

from src.providers.platform import TARGET_INFO
from src.plugins.github.models import Subscription


async def list_subscriptions(info: TARGET_INFO) -> list[Subscription]:
    return await Subscription.from_info(info)


SUBSCRIPTIONS: TypeAlias = Annotated[list[Subscription], Depends(list_subscriptions)]
"""List subscriptions for the current event target."""
