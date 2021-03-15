#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-15 23:40:04
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-16 00:06:26
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel as _BaseModel

from . import BaseModel


class HookConfig(_BaseModel):
    url: str
    content_type: str
    secret: Optional[str] = None
    insecure_ssl: bool


class HookResponse(_BaseModel):
    code: Optional[int]
    status: str
    message: Optional[str]


class Hook(BaseModel):
    type: str
    id: int
    name: str
    active: bool
    events: List[str]
    config: HookConfig
    updated_at: datetime
    created_at: datetime
    url: str
    test_url: str
    ping_url: str
    last_response: HookResponse
