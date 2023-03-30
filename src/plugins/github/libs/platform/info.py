#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 06:16:48
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 23:40:16
@Description    : Platform info
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Literal, TypedDict

USER_INTEGER_TYPES = Literal["qq"]
USER_STRING_TYPES = Literal["qqguild"]

GROUP_INTEGER_TYPES = Literal["qq"]
GROUP_STRING_TYPES = Literal["qqguild"]


class UserIntInfo(TypedDict):
    """User info with integer id"""

    type: USER_INTEGER_TYPES
    user_id: int


class UserStrInfo(TypedDict):
    """User info with string id"""

    type: USER_STRING_TYPES
    user_id: str


UserInfo = UserIntInfo | UserStrInfo
"""User info"""


class GroupIntInfo(TypedDict):
    """Group info with integer id"""

    type: GROUP_INTEGER_TYPES
    group_id: int


class GroupStrInfo(TypedDict):
    """Group info with string id"""

    type: GROUP_STRING_TYPES
    group_id: str


GroupInfo = GroupIntInfo | GroupStrInfo
"""Group info"""
