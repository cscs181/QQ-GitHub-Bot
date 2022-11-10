#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-11-07 06:16:48
@LastEditors    : yanyongyu
@LastEditTime   : 2022-11-07 06:18:00
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Literal, TypedDict

USER_INTEGER_TYPES = Literal["qq"]
USER_STRING_TYPES = Literal["qqguild"]

GROUP_INTEGER_TYPES = Literal["qq"]
GROUP_STRING_TYPES = Literal["qqguild"]


class UserIntInfo(TypedDict):
    type: USER_INTEGER_TYPES
    user_id: int


class UserStrInfo(TypedDict):
    type: USER_STRING_TYPES
    user_id: str


UserInfo = UserIntInfo | UserStrInfo


class GroupIntInfo(TypedDict):
    type: GROUP_INTEGER_TYPES
    group_id: int


class GroupStrInfo(TypedDict):
    type: GROUP_STRING_TYPES
    group_id: str


GroupInfo = GroupIntInfo | GroupStrInfo
