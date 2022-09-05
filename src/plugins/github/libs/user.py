#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:32:25
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-05 11:57:25
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Type, Literal, overload

from .models import QQUser, QQGuildUser

USER_TYPES = Literal["qq", "qqguild"]
USER_MODELS = Type[QQUser] | Type[QQGuildUser]
USER_DATA = QQUser | QQGuildUser
USER_TYPE_MAPPINGS: dict[USER_TYPES, USER_MODELS] = {
    "qq": QQUser,
    "qqguild": QQGuildUser,
}


@overload
async def get_user(type: Literal["qq"], user_id: int) -> QQUser:
    ...


@overload
async def get_user(type: Literal["qqguild"], user_id: str) -> QQGuildUser:
    ...


async def get_user(type: USER_TYPES, user_id: int | str) -> USER_DATA:
    model = USER_TYPE_MAPPINGS[type]
    return await model.get(user_id=user_id)


@overload
async def create_or_update_user(
    type: Literal["qq"], user_id: int, access_token: str
) -> QQUser:
    ...


@overload
async def create_or_update_user(
    type: Literal["qqguild"], user_id: str, access_token: str
) -> QQGuildUser:
    ...


async def create_or_update_user(
    type: USER_TYPES, user_id: int | str, access_token: str
) -> USER_DATA:
    model = USER_TYPE_MAPPINGS[type]
    data, _ = await model.update_or_create(
        user_id=user_id, defaults={"access_token": access_token}
    )
    return data
