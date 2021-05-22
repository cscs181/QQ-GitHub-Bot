#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-05-23 01:18:20
@LastEditors    : yanyongyu
@LastEditTime   : 2021-05-23 02:04:10
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import re
import json
import glob
from typing import List, Optional
from dataclasses import dataclass, asdict

from . import redis

SUBSCRIBE_GROUP_REPO_FORMAT = "github_subscribe_{group_id}_{repo_name}"
SUBSCRIBE_GROUP_GLOB_PATTERN = "github_subscribe_{group_id}_*"
SUBSCRIBE_GROUP_PATTERN = r"^github_subscribe_{group_id}_(?P<repo_name>.*)$"
SUBSCRIBE_REPO_GLOB_PATTERN = "github_subscribe_*_{repo_name}"
SUBSCRIBE_REPO_PATTERN = r"^github_subscribe_(?P<group_id>.*?)_{repo_name}$"


@dataclass
class SubscribeConfig:
    pushes: bool = True
    issues: bool = True
    issue_comments: bool = True
    pull_requests: bool = True


def set_subscribe(group_id: str, repo_name: str, **kwargs) -> Optional[bool]:
    return redis.set(
        SUBSCRIBE_GROUP_REPO_FORMAT.format(group_id=group_id,
                                           repo_name=repo_name),
        json.dumps(asdict(SubscribeConfig(**kwargs))))


def delete_subscribe(group_id: str, repo_name: str) -> int:
    return redis.delete(
        SUBSCRIBE_GROUP_REPO_FORMAT.format(group_id=group_id,
                                           repo_name=repo_name))


def exists_subscribe(group_id: str, repo_name: str) -> int:
    return redis.exists(
        SUBSCRIBE_GROUP_REPO_FORMAT.format(group_id=group_id,
                                           repo_name=repo_name))


def get_subscribe(group_id: str, repo_name: str) -> Optional[SubscribeConfig]:
    value = redis.get(
        SUBSCRIBE_GROUP_REPO_FORMAT.format(group_id=group_id,
                                           repo_name=repo_name))
    return value if value is None else SubscribeConfig(**json.loads(value))


def get_group_subscribe(group_id: str) -> List[str]:
    subscribed = redis.keys(
        SUBSCRIBE_GROUP_GLOB_PATTERN.format(group_id=glob.escape(group_id)))
    return [
        match.group("repo_name")
        for key in subscribed
        if (match := re.match(SUBSCRIBE_GROUP_PATTERN, key.decode()))
    ]


def get_repo_subscribe(repo_name: str) -> List[str]:
    subscribed = redis.keys(
        SUBSCRIBE_REPO_GLOB_PATTERN.format(repo_name=glob.escape(repo_name)))
    return [
        match.group("group_id")
        for key in subscribed
        if (match := re.match(SUBSCRIBE_REPO_PATTERN, key.decode()))
    ]
