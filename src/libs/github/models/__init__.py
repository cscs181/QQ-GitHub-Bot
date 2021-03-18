#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 01:34:31
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-19 01:23:51
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from contextvars import ContextVar
from typing import Type, TypeVar

from pydantic import BaseModel as _BaseModel, Field

from ..request import Requester

_T = TypeVar("_T", bound="BaseModel")

_requester: ContextVar[Requester] = ContextVar("_requester")


class BaseModel(_BaseModel):
    requester: Requester = Field(default_factory=lambda: _requester.get())

    def __init__(self, **data):
        hd = None
        if "requester" in data:
            hd = _requester.set(data["requester"])
        super(BaseModel, self).__init__(**data)
        if hd:
            _requester.reset(hd)

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    async def close(self):
        await self.requester.close()

    @classmethod
    def parse_obj(cls: Type[_T], obj: dict) -> _T:
        return super(BaseModel, cls).parse_obj(obj)  # type: ignore


from .user import User
from .issue import Issue
from .label import Label
from .license import License
from .hook import Hook, HookConfig
from .permissions import Permissions
from .organization import Organization
from .repository import LazyRepository, Repository
