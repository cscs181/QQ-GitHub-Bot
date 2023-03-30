#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:15:21
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 18:23:38
@Description    : Getting status of the bot and the mechine
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

import psutil
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters import Bot

if TYPE_CHECKING:
    from psutil._common import sdiskusage

CURRENT_TIMEZONE = datetime.now().astimezone().tzinfo

driver = get_driver()

# bot status
_nonebot_run_time: datetime
_bot_connect_time: Dict[str, datetime] = {}


@driver.on_startup
async def _():
    global _nonebot_run_time
    _nonebot_run_time = datetime.now(CURRENT_TIMEZONE)


@driver.on_bot_connect
async def _(bot: Bot):
    _bot_connect_time[bot.self_id] = datetime.now(CURRENT_TIMEZONE)


@driver.on_bot_disconnect
async def _(bot: Bot):
    _bot_connect_time.pop(bot.self_id, None)


def get_nonebot_run_time() -> datetime:
    """Get the time when NoneBot started running."""
    try:
        return _nonebot_run_time
    except NameError:
        raise RuntimeError("NoneBot not running!") from None


def get_bot_connect_time() -> Dict[str, datetime]:
    """Get the time when the bot connected to the server."""
    return _bot_connect_time


def get_cpu_status() -> float:
    """Get the CPU usage status."""
    return psutil.cpu_percent(interval=0.3)  # type: ignore


def per_cpu_status() -> List[float]:
    """Get the CPU usage status of each core."""
    return psutil.cpu_percent(interval=0.3, percpu=True)  # type: ignore


def get_memory_status():
    """Get the memory usage status."""
    return psutil.virtual_memory()


def get_swap_status():
    """Get the swap usage status."""
    return psutil.swap_memory()


def _get_disk_usage(path: str) -> Optional["sdiskusage"]:
    try:
        return psutil.disk_usage(path)
    except Exception as e:
        logger.warning(f"Could not get disk usage for {path}: {e!r}")


def get_disk_usage() -> Dict[str, "sdiskusage"]:
    """Get the disk usage status."""
    disk_parts = psutil.disk_partitions()
    return {
        d.mountpoint: usage
        for d in disk_parts
        if (usage := _get_disk_usage(d.mountpoint))
    }


def get_uptime() -> datetime:
    """Get the uptime of the mechine."""
    return datetime.fromtimestamp(psutil.boot_time(), tz=CURRENT_TIMEZONE)
