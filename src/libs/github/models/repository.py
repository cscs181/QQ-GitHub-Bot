#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 01:33:54
@LastEditors    : yanyongyu
@LastEditTime   : 2021-03-11 01:43:27
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pydantic import BaseModel


class LazyRepository(BaseModel):
    full_name: str

    class Config:
        extra = "allow"


class Repository(LazyRepository):
    id: int
    node_id: str
    name: str
    # TODO
