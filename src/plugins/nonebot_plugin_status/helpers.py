"""
@Author         : yanyongyu
@Date           : 2022-10-15 08:08:41
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 18:24:49
@Description    : Template rendering helpers
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
