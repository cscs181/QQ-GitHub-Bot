#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 01:34:31
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-16 00:05:53
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import inspect
from typing import Any, Type, Union, TypeVar

from pydantic import BaseModel as _BaseModel, root_validator

from ..request import Requester

_T = TypeVar("_T", bound="BaseModel")


class BaseModel(_BaseModel):
    requester: Requester

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def apply_requester(cls, values: dict) -> dict:
        assert "requester" in values, "requester needed"
        for name, info in cls.__fields__.items():
            is_model = inspect.isclass(info.type_) and issubclass(
                info.type_, BaseModel)
            is_generic = (
                hasattr(info.type_, "__origin__") and
                info.type_.__origin__ is Union and  # type: ignore
                any(issubclass(x, BaseModel)
                    for x in info.type_.__args__)  # type: ignore
            )
            if name in values and (is_model or is_generic):
                if isinstance(values[name], dict):
                    values[name]["requester"] = values["requester"]
                elif isinstance(values[name], list):
                    for value in values[name]:
                        value["requester"] = values["requester"]
        return values

    async def close(self):
        await self.requester.close()

    @classmethod
    def parse_obj(cls: Type[_T], obj: Any) -> _T:
        return super(BaseModel, cls).parse_obj(obj)  # type: ignore


from .user import User
from .issue import Issue
from .label import Label
from .license import License
from .hook import Hook, HookConfig
from .permissions import Permissions
from .organization import Organization
from .repository import LazyRepository, Repository
