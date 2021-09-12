#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-23 00:30:58
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-23 00:54:40
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import json
from typing import Optional
from datetime import timedelta
from dataclasses import dataclass

from . import redis

MESSAGE_ID_FORMAT = "github_message_{message_id}"


@dataclass
class MessageInfo:
    owner: str
    repo: str
    number: int


def set_message_info(
    message_id: str, owner: str, repo: str, number: int
) -> Optional[bool]:
    return redis.set(
        MESSAGE_ID_FORMAT.format(message_id=message_id),
        json.dumps({"owner": owner, "repo": repo, "number": number}),
        timedelta(days=3),
    )


def delete_message_info(message_id: str) -> int:
    return redis.delete(MESSAGE_ID_FORMAT.format(message_id=message_id))


def exists_message_info(message_id: str) -> int:
    return redis.exists(MESSAGE_ID_FORMAT.format(message_id=message_id))


def get_message_info(message_id: str) -> Optional[MessageInfo]:
    value = redis.get(MESSAGE_ID_FORMAT.format(message_id=message_id))
    return value if value is None else MessageInfo(**json.loads(value))
