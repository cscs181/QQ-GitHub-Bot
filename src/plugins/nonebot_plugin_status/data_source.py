#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:15:21
@LastEditors    : yanyongyu
@LastEditTime   : 2022-08-13 08:20:43
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import time
from datetime import timedelta
from typing import Dict, List, Optional

import psutil
from nonebot.log import logger


def cpu_status() -> float:
    return psutil.cpu_percent(interval=1)  # type: ignore


def per_cpu_status() -> List[float]:
    return psutil.cpu_percent(interval=1, percpu=True)  # type: ignore


def memory_status() -> float:
    return psutil.virtual_memory().percent


def _get_disk_usage(path: str) -> Optional[psutil._common.sdiskusage]:
    try:
        return psutil.disk_usage(path)
    except Exception as e:
        logger.warning(f"Could not get disk usage for {path}: {e!r}")


def disk_usage() -> Dict[str, psutil._common.sdiskusage]:
    disk_parts = psutil.disk_partitions()
    return {
        d.mountpoint: usage
        for d in disk_parts
        if (usage := _get_disk_usage(d.mountpoint))
    }


def uptime() -> timedelta:
    diff = time.time() - psutil.boot_time()
    return timedelta(seconds=diff)


if __name__ == "__main__":
    print(cpu_status())
    print(memory_status())
    print(disk_usage())
