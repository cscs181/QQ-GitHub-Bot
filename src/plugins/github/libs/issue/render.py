#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-05-14 17:09:12
@LastEditors    : yanyongyu
@LastEditTime   : 2021-05-14 18:26:47
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Any
from pathlib import Path
from inspect import isclass
from datetime import datetime

import jinja2
import humanize

from src.libs.github.models import Issue

env = jinja2.Environment(loader=jinja2.FileSystemLoader(Path(__file__).parent),
                         enable_async=True)


def classname(value: Any) -> str:
    return value.__name__ if isclass(value) else type(value).__name__


def relative_time(value: datetime):
    return humanize.naturaltime(datetime.now(value.tzinfo) - value)


env.filters["classname"] = classname
env.filters["relative_time"] = relative_time


async def issue_to_html(owner: str, repo_name: str, issue: Issue) -> str:
    template = env.get_template("issue.html")
    timeline = await issue.get_timeline()
    return await template.render_async(owner=owner,
                                       repo_name=repo_name,
                                       issue=issue,
                                       timeline=timeline)
    # return HTML.format(owner=escape(owner),
    #                    repo_name=escape(repo_name),
    #                    title=escape(issue.title),
    #                    number=issue.number,
    #                    status=escape(issue.state),
    #                    comments=issue.comments)
