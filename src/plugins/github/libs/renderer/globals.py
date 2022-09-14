#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 16:09:04
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 16:13:09
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from githubkit.rest import Issue

from src.plugins.github.utils import get_bot


def get_issue_timeline(owner: str, repo: str, issue: Issue):
    bot = get_bot()
    return bot.github.paginate(
        bot.rest.issues.async_list_events_for_timeline,
        owner=owner,
        repo=repo,
        issue_number=issue.number,
    )
