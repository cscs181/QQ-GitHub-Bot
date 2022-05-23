#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:15:21
@LastEditors    : yanyongyu
@LastEditTime   : 2022-05-23 04:38:37
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import time
from typing import Dict, List
from datetime import timedelta

import psutil


def cpu_status() -> float:
    return psutil.cpu_percent(interval=1)  # type: ignore


def per_cpu_status() -> List[float]:
    return psutil.cpu_percent(interval=1, percpu=True)  # type: ignore


def memory_status() -> float:
    return psutil.virtual_memory().percent


def disk_usage() -> Dict[str, psutil._common.sdiskusage]:
    disk_parts = psutil.disk_partitions()
    return {d.mountpoint: psutil.disk_usage(d.mountpoint) for d in disk_parts}


def uptime() -> timedelta:
    diff = time.time() - psutil.boot_time()
    return timedelta(seconds=diff)


if __name__ == "__main__":
    print(cpu_status())
    print(memory_status())
    print(disk_usage())
