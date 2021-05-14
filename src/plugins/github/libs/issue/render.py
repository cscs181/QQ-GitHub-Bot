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

from html import escape
from pathlib import Path

from src.libs.github.models import Issue

with (Path(__file__).parent / "issue.html").open("r") as f:
    HTML = f.read()


def issue_to_html(owner: str, repo_name: str, issue: Issue):
    return HTML.format(owner=escape(owner),
                       repo_name=escape(repo_name),
                       title=escape(issue.title),
                       number=issue.number,
                       status=escape(issue.state),
                       comments=issue.comments)
