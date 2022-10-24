#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:15:21
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-24 06:40:10
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import time
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

import psutil
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters import Bot

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
    try:
        return _nonebot_run_time
    except NameError:
        raise RuntimeError("NoneBot not running!") from None


def get_bot_connect_time() -> Dict[str, datetime]:
    return _bot_connect_time


# mechine status
def get_cpu_status() -> float:
    return psutil.cpu_percent(interval=0.3)  # type: ignore


def per_cpu_status() -> List[float]:
    return psutil.cpu_percent(interval=0.3, percpu=True)  # type: ignore


def get_memory_status():
    return psutil.virtual_memory()


def get_swap_status():
    return psutil.swap_memory()


def _get_disk_usage(path: str) -> Optional[psutil._common.sdiskusage]:
    try:
        return psutil.disk_usage(path)
    except Exception as e:
        logger.warning(f"Could not get disk usage for {path}: {e!r}")


def get_disk_usage() -> Dict[str, psutil._common.sdiskusage]:
    disk_parts = psutil.disk_partitions()
    return {
        d.mountpoint: usage
        for d in disk_parts
        if (usage := _get_disk_usage(d.mountpoint))
    }


def get_uptime() -> datetime:
    return datetime.fromtimestamp(psutil.boot_time(), tz=CURRENT_TIMEZONE)
