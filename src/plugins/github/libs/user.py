#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:32:25
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-06 12:06:18
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Any, Literal, overload

from src.plugins.github.models import User

USER_INTEGER_TYPES = Literal["qq"]
USER_STRING_TYPES = Literal["qqguild"]
USER_TYPES = USER_INTEGER_TYPES | USER_STRING_TYPES

TYPE_FIELD_MAPPINGS: dict[USER_TYPES, str] = {"qq": "qq_id", "qqguild": "qqguild_id"}


@overload
async def get_user(type: USER_INTEGER_TYPES, user_id: int) -> User:
    ...


@overload
async def get_user(type: USER_STRING_TYPES, user_id: str) -> User:
    ...


async def get_user(type: USER_TYPES, user_id: int | str) -> User:
    if not (field := TYPE_FIELD_MAPPINGS.get(type)):
        raise ValueError(f"Invalid user type {type}")
    return await User.get(**{field: user_id})


@overload
async def create_or_update_user(
    type: USER_INTEGER_TYPES, user_id: int, **data: Any
) -> User:
    ...


@overload
async def create_or_update_user(
    type: USER_STRING_TYPES, user_id: str, **data: Any
) -> User:
    ...


async def create_or_update_user(
    type: USER_TYPES, user_id: int | str, **data: Any
) -> User:
    if not (field := TYPE_FIELD_MAPPINGS.get(type)):
        raise ValueError(f"Invalid user type {type}")

    user, _ = await User.update_or_create(**{field: user_id}, defaults=data)
    return user


@overload
async def delete_user(type: USER_INTEGER_TYPES, user_id: int) -> None:
    ...


@overload
async def delete_user(type: USER_STRING_TYPES, user_id: str) -> None:
    ...


async def delete_user(type: USER_TYPES, user_id: int | str) -> None:
    user: User = await get_user(type, user_id)  # type: ignore
    await user.delete()
