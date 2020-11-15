#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:15:21
@LastEditors    : yanyongyu
@LastEditTime   : 2020-10-04 15:33:30
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Dict

import psutil


def cpu_status() -> float:
    return psutil.cpu_percent(interval=1)  # type: ignore


def memory_status() -> float:
    return psutil.virtual_memory().percent


def disk_usage() -> Dict[str, psutil._common.sdiskusage]:
    disk_parts = psutil.disk_partitions()
    disk_usages = {
        d.mountpoint: psutil.disk_usage(d.mountpoint) for d in disk_parts
    }
    return disk_usages


if __name__ == "__main__":
    print(cpu_status())
    print(memory_status())
    print(disk_usage())
