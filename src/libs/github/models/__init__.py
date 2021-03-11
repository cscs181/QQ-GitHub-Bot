#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 01:34:31
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-11 17:00:51
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pydantic import BaseModel

from ..request import Requester


class BaseModel(BaseModel):
    _requester: Requester

    class Config:
        extra = "allow"
        underscore_attrs_are_private = True


from .user import User
from .issue import Issue
from .label import Label
from .license import License
from .permissions import Permissions
from .organization import Organization
from .repository import LazyRepository, Repository
