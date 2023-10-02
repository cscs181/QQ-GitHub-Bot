"""
@Author         : yanyongyu
@Date           : 2022-10-14 17:04:02
@LastEditors    : yanyongyu
@LastEditTime   : 2023-10-02 16:10:56
@Description    : Multi pod status plugin
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import contextlib

from nonebot.matcher import Matcher

from src.plugins.nonebot_plugin_status import status_config

from .data_source import get_all_status


async def server_status(matcher: Matcher):
    """Multi pod status matcher handler"""
    await matcher.finish(message=await get_all_status())


if not status_config.server_status_enabled:
    from . import common as common

    with contextlib.suppress(ImportError):
        import nonebot.adapters.onebot.v11  # noqa: F401

        from . import onebot_v11 as onebot_v11
