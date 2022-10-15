#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-10-15 08:08:41
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-15 12:00:21
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from datetime import datetime, timedelta

import humanize


def relative_time(time: datetime) -> timedelta:
    return datetime.now().astimezone() - time.astimezone()


def humanize_date(time: datetime) -> str:
    return humanize.naturaldate(time.astimezone())


def humanize_delta(delta: timedelta) -> str:
    return humanize.precisedelta(delta, minimum_unit="minutes")
