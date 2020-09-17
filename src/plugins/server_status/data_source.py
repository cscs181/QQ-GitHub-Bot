#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-09-18 00:15:21
@LastEditors    : yanyongyu
@LastEditTime   : 2020-09-18 00:47:13
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import psutil


def cpu_status():
    return psutil.cpu_percent(interval=1)


def memory_status():
    return psutil.virtual_memory().percent


if __name__ == "__main__":
    print(cpu_status())
    print(memory_status())
