"""
@Author         : yanyongyu
@Date           : 2022-10-26 15:35:46
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-08 17:12:43
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot.matcher import Matcher

from src.providers.platform import TARGET_INFO, TargetType


async def stop_unavailable_target(matcher: Matcher, target_info: TARGET_INFO) -> None:
    if target_info.type in (TargetType.QQGUILD_USER):
        await matcher.finish("当前场景不支持此操作！")


async def bypass_create(matcher: Matcher) -> None:
    if matcher.get_arg("full_name") is not None:
        matcher.skip()
