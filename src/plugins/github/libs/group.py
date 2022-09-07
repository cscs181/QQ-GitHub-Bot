#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-06 09:20:35
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-06 12:06:26
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2022-09-05 11:32:25
@LastEditors    : yanyongyu
@LastEditTime   : 2022-09-06 07:50:48
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"


from typing import Any, Literal, overload

from src.plugins.github.models import Group

GROUP_INTEGER_TYPES = Literal["qq"]
GROUP_STRING_TYPES = Literal["qqguild"]
GROUP_TYPES = GROUP_INTEGER_TYPES | GROUP_STRING_TYPES

TYPE_FIELD_MAPPINGS: dict[GROUP_TYPES, str] = {
    "qq": "qq_group",
    "qqguild": "qqguild_channel",
}


@overload
async def get_group(type: GROUP_INTEGER_TYPES, group_id: int) -> Group:
    ...


@overload
async def get_group(type: GROUP_STRING_TYPES, group_id: str) -> Group:
    ...


async def get_group(type: GROUP_TYPES, group_id: int | str) -> Group:
    if not (field := TYPE_FIELD_MAPPINGS.get(type)):
        raise ValueError(f"Invalid group type {type}")
    return await Group.get(**{field: group_id})


@overload
async def create_or_update_group(
    type: GROUP_INTEGER_TYPES, group_id: int, **data: Any
) -> Group:
    ...


@overload
async def create_or_update_group(
    type: GROUP_STRING_TYPES, group_id: str, **data: Any
) -> Group:
    ...


async def create_or_update_group(
    type: GROUP_TYPES, group_id: int | str, **data: Any
) -> Group:
    if not (field := TYPE_FIELD_MAPPINGS.get(type)):
        raise ValueError(f"Invalid group type {type}")

    group, _ = await Group.update_or_create(**{field: group_id}, defaults=data)
    return group


@overload
async def delete_group(type: GROUP_INTEGER_TYPES, group_id: int) -> None:
    ...


@overload
async def delete_group(type: GROUP_STRING_TYPES, group_id: str) -> None:
    ...


async def delete_group(type: GROUP_TYPES, group_id: int | str) -> None:
    group: Group = await get_group(type, group_id)  # type: ignore
    await group.delete()
