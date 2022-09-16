#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-14 03:31:15
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-14 11:20:57
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

OWNER_REGEX = r"(?P<owner>[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)"
REPO_REGEX = r"(?P<repo>[a-zA-Z0-9_\-\.]+)"
FULLREPO_REGEX = rf"{OWNER_REGEX}/{REPO_REGEX}"
COMMIT_HASH_REGEX = r"(?P<commit>[0-9a-f]{5,40})"
ISSUE_REGEX = r"(?P<issue>\d+)"
PULL_REGEX = r"(?P<pull>\d+)"

GITHUB_LINK_REGEX = r"github\.com"
GITHUB_REPO_LINK_REGEX = rf"{GITHUB_LINK_REGEX}/{FULLREPO_REGEX}"
GITHUB_COMMIT_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/commit/{COMMIT_HASH_REGEX}"
GITHUB_ISSUE_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/issues/{ISSUE_REGEX}"
GITHUB_PR_LINK_REGEX = rf"{GITHUB_REPO_LINK_REGEX}/pull/{PULL_REGEX}"
GITHUB_ISSUE_OR_PR_LINK_REGEX = (
    rf"{GITHUB_REPO_LINK_REGEX}/(?:issues|pull)/{ISSUE_REGEX}"
)
GITHUB_PR_COMMIT_LINK_REGEX = rf"{GITHUB_PR_LINK_REGEX}/commits/{COMMIT_HASH_REGEX}"