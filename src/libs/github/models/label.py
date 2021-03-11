#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 16:59:39
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-11 17:00:37
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from . import BaseModel


class Label(BaseModel):
    id: int
    node_id: str
    url: str
    name: str
    description: str
    color: str
    default: bool
