#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 16:59:39
@LastEditors    : yanyongyu
@LastEditTime   : 2021-04-20 19:11:53
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from typing import Optional

from . import BaseModel


class Label(BaseModel):
    id: int
    node_id: str
    url: str
    name: str
    description: Optional[str]
    color: str
    default: bool
