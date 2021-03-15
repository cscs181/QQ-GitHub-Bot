#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-14 10:53:42
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-16 00:57:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional
from datetime import timedelta

from .. import redis

GITHUB_BIND_FORMAT = "github_bind_{group_id}"
USER_STATE_FORMAT = "github_state_{state}"
USER_TOKEN_FORMAT = "github_token_{user_id}"
REPO_HOOK_FORMAT = "github_hook_{repo_name}"


def set_group_bind_repo(group_id: int, full_name: str) -> Optional[bool]:
    return redis.set(GITHUB_BIND_FORMAT.format(group_id=group_id), full_name)


def delete_group_bind_repo(group_id: int) -> int:
    return redis.delete(GITHUB_BIND_FORMAT.format(group_id=group_id))


def exists_group_bind_repo(group_id: int) -> int:
    return redis.exists(GITHUB_BIND_FORMAT.format(group_id=group_id))


def get_group_bind_repo(group_id: int) -> Optional[str]:
    value = redis.get(GITHUB_BIND_FORMAT.format(group_id=group_id))
    return value if value is None else value.decode()


def set_state_bind_user(user_id: str, state: int) -> Optional[bool]:
    return redis.set(USER_STATE_FORMAT.format(state=state), user_id,
                     timedelta(minutes=5))


def get_state_bind_user(state: int) -> Optional[str]:
    value = redis.get(USER_STATE_FORMAT.format(state=state))
    return value if value is None else value.decode()


def set_user_token(user_id: str, token: str) -> Optional[bool]:
    return redis.set(USER_TOKEN_FORMAT.format(user_id=user_id), token)


def delete_user_token(user_id: str) -> int:
    return redis.delete(USER_TOKEN_FORMAT.format(user_id=user_id))


def exists_user_token(user_id: str) -> int:
    return redis.exists(USER_TOKEN_FORMAT.format(user_id=user_id))


def get_user_token(user_id: str) -> Optional[str]:
    value = redis.get(USER_TOKEN_FORMAT.format(user_id=user_id))
    return value if value is None else value.decode()


def set_repo_hook(hook_id: str, full_name: str) -> Optional[bool]:
    return redis.set(REPO_HOOK_FORMAT.format(repo_name=full_name), hook_id)


def delete_repo_hook(full_name: str) -> int:
    return redis.delete(REPO_HOOK_FORMAT.format(repo_name=full_name))


def exists_repo_hook(full_name: str) -> int:
    return redis.exists(REPO_HOOK_FORMAT.format(repo_name=full_name))


def get_repo_hook(full_name: str) -> Optional[str]:
    value = redis.get(REPO_HOOK_FORMAT.format(repo_name=full_name))
    return value if value is None else value.decode()
